# Rails-Migration-Exporter
Use MySQL Workbench to generate Ruby on Rails version 4.2 migration files.

# Dependencies
This plugin depends on the python module 'inflection' to pluralize words, and convert names between CamelCase and underscore_case. To install inflection use
'pip install inflection'
If you do not have pip installed, follow the instructions at [Install pip](https://packaging.python.org/installing/#id10) 

# Installation
 1. Install the dependencies
 2. Run MySQL Workbench and click on the Scipting -> Install Plugin/Module... menu option.
 3. Open the project folder and select the file 'export-rails-4-migrations_grt.py'.

# How To Use
To use the tool go to the menu and select Tools -> Catalog -> Export Rails 4.2 Migration
Select the folder you wish to place the migration files in and click open.
If all goes well, your migration files will be in the selected folder.

# Features
 * Handles the most common MySQL data types.
 * Handles foreign keys.
 * Orders migration files, so that if a table B has foreign key to table A, table A is create before table B. The algorithm work even if table A and table B have foreign keys to eachother. See the section on algorithm for more information.
 * Handles full and partial indexes with unique or fulltext. 

# Limitations
This plugin does a reasonable job exporting a database schema to Rails. However, the Rails framework places limitations on the database design. For instance, Rails does not support a primary key other than an auto-incrementing integer named 'id'. Therefore, should the exporter detect a non-standard primary key, it will alert you and stop execution. Also, all foreign key must end with '_id'.
Remember to design your database the Rails way.

# Supported Column Types
 * VARCHAR
 * TINYINT (as boolean only)
 * SMALLINT
 * MEDIUMINT
 * INT
 * BIGINT
 * FLOAT
 * TEXT
 * DECIMAL
 * BLOB
 * DATE
 * TIME
 * DATETIME
 * TIMESTAMP

# How It Works For the New Developer
The following is a high level overview of how this plugin works. This is intended for the new MySQL Workbench developer who would like to modify this plugin to suit their needs, but doesn't know where to start. 

The order of migration files is important. If table B has a foreign key to table A, then table A must be created before table B. Otherwise, an error will occur since a foreign key cannot be made to a table that does not exist. We can say that table B depends on table A. Sorting the tables, such that all the depencies come before the dependent is accomplished by topoligical sorting where the tables act as vertices, and foreign keys act as edges in a directed graph. Furthermore, the tables can only be topologically sorted if there are no cycles in the graph. If there are cycles (with exception to a recursive or unary, cycle to self), the cycle must be broken/resolved. The algorithm accomplishes this by removing the foreign key from the table, and adding the key to a list that will eventually be added to the file "AddResolvedForeignKeys.".

Ordering the tables topologically and breaking cycles is made more difficult because the data provided by MySQL Workbench is provided as non-copyable read-only data. A cycle cannot be broken if the foreign key cannot be removed. My solution was to create my own classes that wrap around the existing objects that MySQL Workbench provides. I used two hashes, one to map between MySQL Workbench tables and my tables, and one to map between MySQL Workbench columns and my columns. By defining these mappings, I could encapsulate their objects inside my own without actually copying anything but the structure of the directed graph. I could then remove foreign keys from my own tables as desired. 

Once the tables are sorted, all that remains is to write them to the migration files. To accomplish this a composite pattern was chosen. With SourceComponent as a base class, SCBlock component as the composite, and SCLine as the leaf. Using this design allows for a very elegant method of composing the source files. It automates indenting the source code, and allows for different sections of the file to be created independently and then added or merged together.
# Author
Bob Dill
Special thanks to Brandon Eckenrode for creating a module to export MySQL Workbench schemas to Laravel migrations. [MySQL Workbench Export Laravel 5 Migrations Plugin](https://github.com/beckenrode/mysql-workbench-export-laravel-5-migrations)
# Available For Hire
If you like this tool, and would like to hire me. Feel free to contact me via [linkedin](https://www.linkedin.com/in/bob-dill-1905a1a0?trk=nav_responsive_tab_profile_pic)
