# TombProspectorsChaliceCompass
Chalice Compass is a tool designed for Bloodborne players, enabling them to search, filter, and manage dungeon data effectively. The project features a graphical user interface built with Tkinter, connected to an packaged SQLite database to store dungeon and equipment information. Users can perform string-based and equipment-based searches, view detailed dungeon notes, and update dungeon statuses.


# Installation Instructions
Prerequisites
Ensure that your system meets the following prerequisites before installing and running the Chalice Compass application:
Windows Operating System
Download the main.exe executable file and ChaliceCompass.db database file.
Step-by-Step Installation
Download the File

For this to run, you only need the ChaliceCompass_(version_number).exe to be downloaded. The rest is for programming purposes
Create a Directory

Create a new folder on your computer where you want to store the application files. For example, you can create a folder named ChaliceCompass on your desktop or any preferred location.
Move Files to Directory
Move the downloaded main.exe executable file into the ChaliceCompass folder.
Move the downloaded ChaliceCompass.db database file into the same ChaliceCompass folder.
Run the Application

Open the ChaliceCompass folder where you placed the files.
Double-click the ChaliceCompass_(version_number).exe file to run the application.

Using the Application
The application window will open, allowing you to search, filter, and manage dungeon data.
Use the equipment type dropdown to filter items and the search functionality to find specific dungeons or equipment.
Update dungeon statuses as needed using the provided buttons.

Troubleshooting
Antivirus Warnings: Some antivirus programs may flag the executable file. If this occurs, you may need to whitelist the file or disable your antivirus temporarily to run the application.
Python: You might need python to run the program.

# Future Plans
It's pretty elementary stuff, but if this tool picks up, here are some improvements I'll need to make.

Integration with External Data Sources: Some way to automate datatransfer from bloodsheets.xlsx
Code Certificate: I need to pay for an evaluation of the code so that my program doesn't get flagged as a virus.
Redis Cache Layer: Implementing a Redis cache to improve read performance and handle higher request rates.
Migration to PostgreSQL: Transitioning to a more robust database system like PostgreSQL to support higher throughput and better performance. 
Move Primary Database to Online Server, keep local copy: This would allow for automatic data updates rather than everyone having their own local copy.
Make more easily accessible and build it to run on different OS.

The Chalice Compass tool aims to assist players in navigating game dungeons more efficiently, ultimately enhancing their gaming experience.

