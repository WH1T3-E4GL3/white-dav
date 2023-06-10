# white-dav
This is a website penetration testing tool for testing webdav server vulnerabilities.




## Author
<a href="https://github.com/WH1T3-E4GL3"><img title="Github" src="https://img.shields.io/badge/WH1T3-E4GL3-brightgreen?style=for-the-badge&logo=github"></a>
## Support
[![Instagram](https://img.shields.io/badge/TELEGRAM-red?style=for-the-badge&logo=telegram)](https://t.me/Ka_KsHi_HaTaKe)       [![Instagram](https://img.shields.io/badge/INSTAGRAM-FOLLOW-green?style=for-the-badge&logo=instagram)](https://www.instagram.com/_vladimir_putin.___/?igshid=YmMyMTA2M2Y=)


# Installation
    $ apt update && apt update -y
    $ apt install git -y
    $ apt install python -y
    $ pip2 install requests
    $ pip install requests
    $ git clone https://github.com/WH1T3-E4GL3/white-dav.git
    $ cd white-dav
    $ git pull
    $ python white-dav.py
    
    
# Note

⚠️Only tests websites with WebDAV vulnerability(Accepts unauthenticated requests)⚠️ 


# WebDAV Testing Script

The WebDAV Testing Script is a Python script designed to assess the vulnerability of a web server to WebDAV (Web Distributed Authoring and Versioning) attacks. WebDAV is an extension to the HTTP protocol that enables collaborative editing and remote file management on web servers.

The script is divided into several functions that perform different actions related to WebDAV testing. Here's an overview of the functionalities provided:

🪲Test URL for WebDAV vulnerability: This function checks a specific URL for the presence of WebDAV vulnerability by attempting to upload a test file to the server. If the upload is successful, the URL is considered vulnerable.

🪲Test multiple URLs from a file: This function reads a file containing a list of URLs and tests each URL for WebDAV vulnerability using the previous function. It generates a report indicating which URLs are vulnerable.

🪲List Directory: This function retrieves and displays the directory listing of a specified URL using the PROPFIND method. It shows the name, size, and last modified date of each file and subdirectory within the directory.

🪲Change Directory: This function allows changing the current working directory by appending a directory name to the base URL.

🪲Upload File: This function uploads a local file to a specified URL using the PUT method. It reports whether the upload was successful or not.

🪲Download File: This function downloads a file from a specified URL using the GET method and saves it to the local system.

🪲Print Working Directory: This function retrieves and displays the current working directory (URL) using the PROPFIND method.

🪲Edit File: This function allows editing a file on the server by retrieving its content, opening it in the Nano text editor, modifying the content, and saving the changes back to the server.

🪲Delete File: This function deletes a file from the server using the DELETE method.

🪲Delete Directory: This function deletes a directory and its contents from the server using the DELETE method.

🪲Copy File: This function copies a file from a source path to a destination path on the server using the COPY method.

🪲Get Server Version: This function retrieves and displays the server version, supported methods, and additional server details using the OPTIONS method.

🪲Delete All Files: This function deletes all files within a specified directory on the server.

🪲Delete Specific Files: This function deletes a list of specific files (separated by commas) on the server.

The script provides a menu-based interface to interact with these functionalities, allowing users to choose the desired action and provide the necessary inputs. It also includes error handling and informative messages to guide the user throughout the process.

To run the script, ensure that the required dependencies (requests, subprocess, xml.etree.ElementTree) are installed. The script can be executed from the command line or integrated into other projects for automated web server testing.

Please note that this script should only be used for ethical purposes with proper authorization. Unauthorized testing of web servers can be illegal and may lead to severe consequences.
