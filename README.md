# MySQL Workbench to Rails 4.2 Migration Exporter
Use MySQL Workbench to generate Ruby on Rails version 4.2 migration files.

# Dependencies
This plugin depends on the python module 'inflection' to pluralize words, and convert names between CamelCase and underscore_case. To install inflection use
'pip install inflection'
If you do not have pip installed, follow the instructions at [install pip](https://packaging.python.org/installing/#id10) 

# How To Use
## Installation
 1. Run MySQL Workbench and click on the Scipting -> Install Plugin/Module... menu option.
 2. Open the project folder and select the file 'export-rails-4-migrations_grt.py'.

## Design the Database the Rails Way
 * Use an auto-incrementing, integer named 'id' for primary keys.
 * Append '_id' to all of your foreign key column names.
 * Do not use composite primary keys, or foreign keys. 

## Run the Plugin
 * Select Tools -> Catalog -> Export Rails 4.2 Migration
 * Select the folder you wish to place the migration files in.

# Features
 * Handles the most common MySQL data types.
 * Handles foreign keys.
 * Handles all four index types: primary, index, unique, and fulltext using all or part of the indexed column.
 * Adjusts timestamps on migration files, so that the files are migrated in topological order, and breaks any cycles. See topological ordering below for more details.

# Topological Ordering
 Suppose that table B has foreign key to table A, then table B depends on table A, and table A must migrate before table B. Topological ordering orders the tables in such a way that for any table its dendents are migrated before the table is migrated. However,  topological sorting is impossible if there are cyclic dependencies. For example, table A depends on table B, and table B depends on table A. If such a case arrises, this plugin removes a foreign key from one of the migration files, breaking the cycle, and then adds that foreign key to a resolve file. The resolve file, add_resolved_foreign_keys, is migrated last. Therefore, for each table, all its columns and foreign keys are placed in its migration file except for those foreign keys that cuase cycles. The keys that cause cycles are moved to the resolve migration file.

# Limitations
 * Must use an auto-incrementing, integer named 'id' for primary keys.
 * All foreign key column names must end with '_id'
 * Cannot use composite primary keys.
 * Cannot use composite foreign keys.

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
 * TIMESTAMPS: Create a column named timestamps, and the created_at and updated_at columns will be created for you.

# Author
 * Bob Dill
 * Special thanks to Laura Williams who helped make this project possible.
 * Special thanks to Brandon Eckenrode for creating a module to export MySQL Workbench schemas to Laravel migrations. [MySQL Workbench Export Laravel 5 Migrations Plugin](https://github.com/beckenrode/mysql-workbench-export-laravel-5-migrations)

# Available For Hire
If you like this tool, and would like to hire me. Feel free to contact me via [linkedin](https://www.linkedin.com/in/bob-dill-1905a1a0?trk=nav_responsive_tab_profile_pic)
