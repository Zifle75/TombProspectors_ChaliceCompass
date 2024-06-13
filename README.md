# TombProspectorsChaliceCompass
Chalice Compass is a tool designed for Bloodborne players, enabling them to search, filter, and manage dungeon data effectively. The project features a graphical user interface built with Tkinter, connected to an packaged SQLite database to store dungeon and equipment information. Users can perform string-based and equipment-based searches, view detailed dungeon notes, and update dungeon statuses. Also no sketchy stuff is happening here. I am not collecting your data or anything, I just want to contribute some of what I know to the community.


# Installation Instructions
I tried to build the exectuably for Windows, Mac, and Linux, but I've only tested it on windows. Theoretically it can do more but leave a comment here if it doesn't work.

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


