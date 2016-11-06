# -*- coding: utf-8 -*-
# MySQL Workbench module
# <description>
# Written in MySQL Workbench 6.3.6

from wb import *
import grt
import sys
import mforms
import datetime
import inflection

ModuleInfo = DefineModule(name='generateRailsMigration',
                         author='Bob Dill',
                          version='0.1')

@ModuleInfo.plugin('wb.util.generateRailsMigration',
                   caption='Export Rails 4.2 Migration',
                   input=[wbinputs.currentCatalog()],
                   groups=['Catalog/Utilities', 'Menu/Catalog'])

@ModuleInfo.export(grt.INT, grt.classes.db_Catalog)

def generateRailsMigration(catalog):
	try:
		exporter = Exporter(catalog)

	except ExportError as e:
		e.show()

	return 0

###############################################################################
#
# Common data structures not supplied by python, but needed for this project
#
###############################################################################
class LinkedListNode:
	def __init__(self, value, prev = None, next = None):
		if (prev):
			prev.next = self
		self.prev = prev
		self.value = value
		if (next):
			next.prev = self
		self.next = next

class LinkedListIter:
	def __init__(self, startNode):
		self.node = startNode

	def next(self):
		if(self.node == None):
			raise StopIteration()

		value = self.node.value
		self.node = self.node.next

		return value
			

	def prev(self):
		if(self.node == None):
			raise StopIteration()

		value = self.node.value
		self.node = self.node.prev

		return value

class LinkedList:
	def __init__(self):
		self.count = 0
		self.head = None
		self.tail = None

	def __iter__(self):
		return self.begin()

	def begin(self):
		return LinkedListIter(self.head)

	def end(self):
		return LinkedListIter(self.tail)

	def toString(self):
		itr = self.begin()
		ret = "["
		try:
			value = itr.next()
			ret += str(value)
			while(True):
				value = itr.next()
				ret += ", " + str(value)
		except StopIteration, si:
			ret += "]" 
			return ret

	def __str__(self):
		return self.toString()

	def __repr__(self):
		return self.toString()

	def __len__(self):
		return self.count

	def __nonzero__(self):
		return len(self)

	def push_back(self, value):
		if(self.tail):
			node = LinkedListNode(value, self.tail)
			self.tail = node
		else:
			self.tail = LinkedListNode(value)
			self.head = self.tail
		self.count += 1

	def push_front(self, value):
		if (self.head):
			node = LinkedListNode(value, None, self.head)
			self.head = node
		else:
			self.head = LinkedListNode(value)
			self.tail = self.head
		self.count += 1

	def back(self):
		return self.tail.value

	def front(self):
		return self.head.value

	def isEmpty(self):
		return self.count == 0

	def pop_back(self):
		value = self.tail.value
		self.tail = self.tail.prev
		if (self.tail == None):
			self.head = None
		self.count -= 1
		return value

	def pop_front(self):
		value = self.head.value
		self.head = self.head.next
		if(self.head == None):
			self.tail = None
		self.count -= 1
		return value

	def display(self):
		node = self.head
		while(node):
			print(node.value)
			node = node.next

class Stack:
	def __init__(self):
		self.linkedList = LinkedList()

	def __str__(self):
		return self.linkedList.toString()

	def __repr__(self):
		return self.linkedList.toString()

	def __len__(self):
		return len(self.linkedList)

	def __nonzero__(self):
		return len(self.linkedList)

	def push_back(self, value):
		self.linkedList.push_back(value)

	def back(self):
		return self.linkedList.back()

	def pop_back(self):
		return self.linkedList.pop_back()

class Queue:
	def __init__(self):
		self.linkedList = LinkedList()

	def __str__(self):
		return self.linkedList.toString()

	def __repr__(self):
		return self.linkedList.toString()

	def __len__(self):
		return len(self.linkedList)

	def __nonzero__(self):
		return len(self.linkedList)

	def push_back(self, value):
		self.linkedList.push_back(value)

	def front(self):
		return self.linkedList.front()

	def pop_front(self):
		return self.linkedList.pop_front()

###############################################################################
#
# The following defines classes used to copy and manipulate the read-only
# tables, columns and foreign keys given by MySQL Workbench. To differentiate
# between these classes and the MySQL workbench classes...
#
###############################################################################

class ExportError(Exception):
	def __init__(self, title, message):
		self.title = title
		self.message = message

	def show(self):
		return mforms.Utilities.show_error(
			self.title,
			self.message,
			'OK', "", "")

tableLookup = {}
columnLookup = {}

class Column:
	def __init__(self, wbColumn):
		self.__wbColumn = wbColumn

	def getAutoIncrement(self):
		return self.__wbColumn.autoIncrement

	# Return the name of the column.
	def getName(self):
		return self.__wbColumn.name

	def getCamelizedName(self, plural = False):
		name = self.__wbColumn.name
		name = inflection.camelize(name)
		if (plural):
			name = inflection.pluralize(name)
		return name

	def getUnderscoredName(self, plural = False):
		name = self.__wbColumn.name
		name = inflection.underscore(name)
		if (plural):
			name = inflection.pluralize(name)
		return name

	def getSymbolName(self):
		return ":" + self.__wbColumn.name

	# Returns the columns type, INT, CHAR, VARCHAR, etc. 
	def getType(self):
		if (self.__wbColumn.simpleType):
			return self.__wbColumn.simpleType.name
		return self.__wbColumn.userType.actualType.name

	# If the type is a char or varchar, this function returns the number of
	# characters that can be stored in the column
	def getLength(self):
		return self.__wbColumn.length

	# The maximum number of digits in a decimal value
	def getPrecision(self):
		return self.__wbColumn.precision

	# Returns the number of digits after the decimal point in a DECIMAL 
	# column type
	def getScale(self):
		return self.__wbColumn.scale
	
	def isNotNull(self):
		return self.__wbColumn.isNotNull

	def defaultValue(self):
		if (self.__wbColumn.defaultValueIsNull):
			return "nil"
		return self.__wbColumn.defaultValue


class ForeignKey:
	def __init__(self, wbfk):
		# Ensure that the name ends with _id
		self.__wbfk = wbfk

	def getName(self):
		return self.__wbfk.name

	def referencedTable(self):
		return getTable(self.__wbfk.referencedTable)
	
	def getOwner(self):
		return getTable(self.__wbfk.owner)

	def numColumns(self):
		return len(self.__wbfk.columns)

	def getFirstColumn(self):
		return getColumn(self.__wbfk.columns[0])

	def getFirstReferencedColumn(self):
		return getColumn(self.__wbfk.columns[0])

	def hasStandardName(self):
		stdName = inflection.underscore(self.__wbfk.referencedTable.name) + "_id"
		colName = self.__wbfk.columns[0].name
		return colName == stdName


class Table:
	def __init__(self, wbTable):
		# Notes
		# Ensure a standard primary key (id integer auto_increment)

		# Store a reference to the wbTable
		self.wbTable = wbTable
		# Define a list of columns.
		self.columns = []
		# Define a list of foreign keys that were removed to prevent cyclic dependencies
		self.resolved_fks = []

		# For each wb column, create and store the exporter column
		for wbColumn in wbTable.columns:
			column = getColumn(wbColumn)
			self.columns.append(column)

		self.assignPrimaryKey()
		
	def assignPrimaryKey(self):
		if (not self.wbTable.primaryKey):
			self.primaryKey = None
		else:
			if (len(self.wbTable.primaryKey.columns) > 1):
				raise ExportError("Composite Primary Key Error", "Table " + self.wbTable.name + " contains a composite primary key. Composite keys are currently not supported by rails and this application. Use a surragate key instead and retry exporting.")
			else:
				self.primaryKey = getColumn(self.wbTable.primaryKey.columns[0].referencedColumn)
				if (self.primaryKey.getName() != "id"):
					print("Got here")
					raise ExportError("Non-standard Primary Key", "Table " + self.wbTable.name + " uses a non-standard name for its primary key. Rename the key to 'id' and retry exporting.")
				if (self.primaryKey.getType() != "INT"): 
					raise ExportError("Non-standard Primary Key", "Table " + self.wbTable.name + " uses a primary key that is not an integer. Change the keys type to integer and retry exporting.")
				if (not self.primaryKey.getAutoIncrement()):
					raise ExportError("Non-standard Primary Key", "Table " + self.wbTable.name + " uses a primary key that is not an auto-incrementing integer. Make the key auto-incrementing, and retry export.")

	def getIndices(self):
		return self.wbTable.indices

	def addForeignKeys(self):
		# Create a list to store the foreign keys.	
		self.foreignKeys = []

		# Loop through all the wb foreign keys and create a list
		# exporter foreign keys from them.
		for wbfk in self.wbTable.foreignKeys:
			if (len(wbfk.columns) != 1):
				raise ExportError("Non-standard Foreign Key", "Table " + self.wbTable.name + " uses a foreign key that does not contain exactly one column. Composite foreign keys are not supported. Change your design to follow the rails convention and retry export.")
			if (wbfk.columns[0].name[-3:] != "_id"):
				raise ExportError("Non-standard Foreign Key", "Table " + self.wbTable.name + " uses a foreign key that is named incorrectly. Ensure that the foreign key ends with '_id', and retry export.")
			fk = ForeignKey(wbfk)
			self.foreignKeys.append(fk)

	def getName(self):
		return self.wbTable.name

	def getClassName(self, plural):
		name = self.wbTable.name
		name = inflection.camelize(name)
		if (plural):
			name = inflection.pluralize(name)
		return name

	def getSymbolName(self, plural):
		name = self.wbTable.name
		name = inflection.underscore(name)
		if (plural):
			name = inflection.pluralize(name)
		return ":" + name

	def getDependencies(self):
		# Create a list to hold the tables this table is
		# dependent upon.
		tables = []

		# Loop through all the foreign keys and create a list
		# of the tables they reference.
		for fk in self.foreignKeys:
			table = fk.referencedTable()
			tables.append(table)
		
		# Return the tables.
		return tables

	def removeDependency(self, table):
		# Create a copy of the list 
		for fk in list(self.foreignKeys):
			if (fk.referencedTable() == table):
				self.foreignKeys.remove(fk)
				self.resolved_fks.append(fk)

	def hasStandardPrimaryKey(self):
		pk = self.primaryKey
		if (pk == None):
			return False

		return (pk.getName()) == 'id' and (pk.getAutoIncrement() == 1) and (pk.getType() == "INT")

class Tables:
	# This function recreates the structure of the directed graph formed by
	# the tables and their connections via foreign keys. A time consuming task.
	def __init__(self, catalog):
		# Define a list of tables.
		self.__tables = []

		# Create and store workbench tables as an exporter tables.
		for wbTable in catalog.schemata[0].tables:
			table = getTable(wbTable)
			self.__tables.append(table)

		# Connect the tables
		for table in self.__tables:
			table.addForeignKeys()

	const_white = 0
	const_grey = 1
	const_black = 2

	# Generate a hash to mark nodes as visited or not visited
	def __createColorHash(self):
		h = {}
		for table in self.__tables:
			h[table] = Tables.const_white
		return h

	def topSortUtil(self, startTable, colorHash, orderQueue):
		pathStack = Stack()
		pathStack.push_back(startTable)

		while(pathStack):
			table = pathStack.back()

			# if this is true, all the children have been visited,
			# mark the table as black, remove it from the search path stack,
			# and add it to the orderQueue
			if(colorHash[table] == Tables.const_grey):
				colorHash[table] = Tables.const_black
				pathStack.pop_back()
				orderQueue.push_back(table)
				continue

			# Mark the table as being explored
			colorHash[table] = Tables.const_grey

			# Push unvisitted adjacent tables onto the stack.
			dependencies = table.getDependencies();
			for dependent in dependencies:
				if(colorHash[dependent] == Tables.const_white):
					pathStack.push_back(dependent)
				if(colorHash[dependent] == Tables.const_grey):
					if (table != dependent):
						table.removeDependency(dependent)

	def topSort(self):
		colorHash = self.__createColorHash()
		orderQueue = Queue()

		for table in self.__tables:
			if(colorHash[table] == Tables.const_white):
				self.topSortUtil(table, colorHash, orderQueue)

		return orderQueue

def getColumn(wbColumn):
	if wbColumn in columnLookup:
		return columnLookup[wbColumn]
	
	column = Column(wbColumn)
	columnLookup[wbColumn] = column
	return column

def getTable(wbTable):
	if wbTable in tableLookup:
		return tableLookup[wbTable]

	table = Table(wbTable)
	tableLookup[wbTable] = table
	return table

###############################################################################
#
# Classes that generate the files and write the DDL in Rail's migration file
# format.
#
###############################################################################


# Using a composite pattern
class SourceComponent(object):
	def __init__(self, name = None):
		self.components = []
		self.name = name

	def add(self, component):
		self.components.append(component)

	# Calls write for 
	def write(self, toFile, indent = 0):
		for component in self.components:
			component.write(toFile, indent)

	def __getitem__(self, key):
		return self.components[key]

	# Returns the number of components
	def __len__(self):
		return len(self.components)

	def find(name):
		if (self.name == name):
			return self

		for comp in self.components:
			ret = comp.find(name)
			if (ret):
				return ret;

		return None

class SCLine(SourceComponent):
	def __init__(self, line):
		self.line = line

	def write(self, toFile, indent):
		toFile.write("  " * indent + self.line + "\n")

class SCFunc(SCLine):
	def __init__(self, funcName, *args):
		line = funcName
		argLen = len(args)
		if (argLen > 0):
			for i in range(0, argLen - 1):
				line += " " + args[i] + ","
			line += " " + args[argLen - 1]

		self.line = line

# :limit - Requests a maximum column length. This is number of characters for :string and :text columns and number of bytes for :binary and :integer columns.
# :default - The column‘s default value. Use nil for NULL.
# :null - Allows or disallows NULL values in the column. This option could have been named :null_allowed.
# :precision - Specifies the precision for a :decimal column.
# :scale - Specifies the scale for a :decimal column.
class SCColumn(SCFunc):
	def __init__(self, column):
		name = column.getName()

		# Special column names that corrospond directly to function in Rails.
		if (name == "timestamps"):
			super(SCColumn, self).__init__("t.timestamps", "null:false")
			return

		# Retrieve the columns simple type
		colType = column.getType()
		funcName = None
		args = [column.getSymbolName()]

		# Thanks to
		# http://stackoverflow.com/questions/11889048/is-there-documentation-for-the-rails-column-types
		if (colType == "VARCHAR"):
			funcName = "t.string"
			length = column.getLength()
			if (length != 255):
				args.append("limit:" + str(length))
		# MySQL workbench ignores the precision on tinyint's. A shame considering TINYINT(1)
		# is a synonym for a boolean, and TINYINT(2) or more is not necessarily treated
		# as a boolean. For now, I will treat any TINYINT as boolean. (as safe default?)
		elif (colType == "TINYINT"):
			funcName = "t.boolean"
		elif (colType == "SMALLINT"):
			funcName = "t.integer"
			args.append("limit: 2")
		elif (colType == "MEDIUMINT"):
			funcName = "t.integer"
			args.append("limit: 3")
		elif (colType == "INT"):
			funcName = "t.integer"
		elif (colType == "BIGINT"):
			funcName = "t.integer"
			args.append("limit: 8")
		elif (colType == "FLOAT"):
			funcName = "t.float"
		elif (colType == "TEXT"):
			funcName = "t.text"
			length = column.getLength();
			if (length != -1):
				args.append("limit: " + str(length))
		elif (colType == "DECIMAL"):
			funcName = "t.decimal"
			precision = column.getPrecision()
			if (precision != -1):
				args.append("precision:" + str(precision))
			scale = column.getScale()
			if (scale != -1):
				args.append("scale:" + str(scale))
		elif (colType == "BLOB"):
			funcName = "t.binary"
			length = column.getLength()
			if (length != -1):
				args.append("limit: " + str(length))
		elif (colType == "DATE"):
			funcName = "t.date"
		elif (colType == "TIME"):
			funcName = "t.time"
		elif (colType == "DATETIME"):
			funcName = "t.datetime"
		elif (colType == "TIMESTAMP"):
			funcName = "t.timestamp"

		if not funcName:
			raise ExportError("Unsupported Column Type", "Columns of type " + colType + " are not supported. Change the column to a supported type and retry export.")

		if (column.isNotNull()):
			args.append("null:false")

		defaultValue = column.defaultValue()
		if (defaultValue != ''):
			args.append("default:" + defaultValue)

		print(colType)
		print(args)
		super(SCColumn, self).__init__(funcName, *args)


class SCBlock(SourceComponent):
	def __init__(self, topLine = None, bottomLine = "end"):
		super(SCBlock, self).__init__()
		self.topLine = topLine
		self.bottomLine = bottomLine

	def write(self, toFile, indent):
		if (self.topLine):
			line = SCLine(self.topLine)
			line.write(toFile, indent)
		super(SCBlock, self).write(toFile, indent + 1)
		if (self.bottomLine):
			line = SCLine(self.bottomLine)
			line.write(toFile, indent)


class SCClass(SCBlock):
	def __init__(self, className, baseClassName = None):
		topLine = None
		if (baseClassName):
			topLine = "class %s < %s" % (className, baseClassName)
		else:
			topLine = "class %s" % (className)
		super(SCClass, self).__init__(topLine)

class SCFuncBlock(SCBlock):
	def __init__(self, funcName, blockVar, *args):
		topLine = funcName
		argLen = len(args)
		if (argLen > 0):
			for i in range(0, argLen - 1):
				topLine += " " + args[i] + ","
			topLine += " " + args[argLen - 1]

		topLine += " do |" + blockVar + "|"
		super(SCFuncBlock, self).__init__(topLine)

class SCCreateTableBlock(SCFuncBlock):
	def __init__(self, table):
		tblName = table.getSymbolName(True)
		if (table.primaryKey):
			super(SCCreateTableBlock, self).__init__("create_table", "t", tblName)
		else:
			super(SCCreateTableBlock, self).__init__("create_table", "t", tblName, "id: false")

# Function Declation Component
class SCFuncDec(SCBlock):
	def __init__(self, funcName):
		topLine = "def " + funcName
		super(SCFuncDec, self).__init__(topLine)

###############################################################################
#
# This section contains classes that represent entire files.
#
###############################################################################

class MultiValuedParam(object):
	def __init__(self):
		self.numParams = 0
		self.params = ""

	def add(self, param):
		if (self.numParams == 0):
			self.params = str(param)
		else:
			self.params += ", " + str(param)

		self.numParams += 1

	def __str__(self):
		return self.params

	def __len__(self):
		return self.numParams

	def __nonzero__(self):
		return self.numParams

# This class simplifies creating the column length parameter
class ColLengthParam(object):
	def __init__(self):
		self.firstColumn = None;
		self.firstLength = 0;
		self.numColumns = 0;
		self.params = "";

	def add(self, column, length):
		if (length == 0):
			return;

		if (self.numColumns == 0):
			self.params =  "length: " + str(length)
			self.firstLength = length
			self.firstColumn = column
		elif (self.numColumns == 1):
			self.params = "length: {" + self.firstColumn + ": " + str(self.firstLength)
			self.params += ", " + column + ": " + str(length)
		else:
			self.params += ", " + column + ": " + str(length)

		self.numColumns += 1 

	def __str__(self):
		if (self.numColumns < 2):
			return self.params
		else:
			return self.params + "}"

	def __len__(self):
		return self.numColumns

	def __nonzero__(self):
		return self.numColumns


class MigrationFile(SourceComponent):
	def __init__(self, table):
		super(MigrationFile, self).__init__()
		clsName = table.getClassName(True)
		
		cls = SCClass("Create" + clsName, "ActiveRecord::Migration")
		func = SCFuncDec("change")
		block = SCCreateTableBlock(table)

		columnSection = SourceComponent()
		# Contains all but the resolved foreign keys
		belongsToSection = SourceComponent()
		# Used for foreign keys that have non-standard name
		addFkSection = SourceComponent()
		addIndexSection = SourceComponent()

		self.addColumns(table, columnSection)
		self.addForeignKeys(table, belongsToSection, addFkSection)
		self.addIndices(table, addIndexSection)

		# Assemble the components
		block.add(columnSection)
		block.add(belongsToSection)
		func.add(block)
		func.add(addIndexSection)
		func.add(addFkSection)
		cls.add(func)
		
		self.add(cls)

	def addIndices(self, table, addIndexSection):
		tblName = table.getSymbolName(True)
		indices = table.getIndices()
		for index in indices:
			if (index.indexType == "PRIMARY"):
				continue

			args = [tblName]


			numColumns = len(index.columns)
			# Should an error or warning be displayed here?
			if (numColumns == 0):
				continue
			elif (numColumns == 1):
				column = index.columns[0]
				colName = column.referencedColumn.name
				args.append(":" + colName)
				if (column.columnLength != 0):
					args.append("length: " + str(column.columnLength))
			else:
				colNameParam = MultiValuedParam()
				colLengthParam = MultiValuedParam()
				# Loop through the columns gathering the necessary parameters
				for column in index.columns:
					colName = column.referencedColumn.name
					colNameParam.add(":" + colName)
					if (column.columnLength != 0):
						colLengthParam.add(colName + ": " + str(column.columnLength))
				
				args.append("[" + str(colNameParam) + "]")
				if (colLengthParam):
					args.append("length: {" + str(colLengthParam) + "}")

			# Add the type if necessary
			if (index.indexType == "UNIQUE"):
				args.append("unique:true")
			elif (index.indexType == "FULLTEXT"):
				args.append("type: :fulltext")

			# Uncomment if you want to preserve the index names
			# args.append("name:'%s'" % (index.name))
			addIndexSection.add(SCFunc("add_index", *args))


	# Plain columns are columns that are not primary keys or foreign keys
	def getPlainColumns(self, table):
		# Generates a list of columns that are not foreign keys
		columns = list(table.columns)
		fks = table.foreignKeys
		for fk in fks:
			col = fk.getFirstColumn()
			columns.remove(col)

		if (table.primaryKey):
			# This handles the case when the primary key is also a foreign key.
			try:
				columns.remove(table.primaryKey)
			except ValueError:
				pass


		return columns

	def addColumns(self, table, section):
		columns = self.getPlainColumns(table)

		# Add the columns to the sec
		for column in columns:
			section.add(SCColumn(column))

	def addForeignKeys(self, table, belongsToSec, addFkSec):
		tblName = table.getSymbolName(True)
		fks = table.foreignKeys

		for fk in fks:
			column = fk.getFirstColumn()
			colName = ":" + column.getName()
			args = [colName[:-3]]

			if (fk.hasStandardName()):
				args.append("foreign_key:true")
			else:
				refName = fk.referencedTable().getSymbolName(True)
				args.append("references: " + refName)

				# Add function to section that adds foreign keys
				func = SCFunc("add_foreign_key", tblName, refName, "column: " + colName)
				addFkSec.add(func)

			if (column.isNotNull()):
				args.append("null:false")

			belongsToSec.add(SCFunc("t.belongs_to", *args))

			args = []

class ResolvedFile(SourceComponent):
	def __init__(self, tables):
		super(ResolvedFile, self).__init__()
		cls = SCClass("AddResolvedForeignKeys", "ActiveRecord::Migration")
		func = SCFuncDec("change")

		cls.add(func)

		# This variable 
		self.resolved = False

		for table in tables:
			fks = table.resolved_fks
			if (fks):
				self.resolved = True
				tableName = table.getSymbolName(True)
				for fk in fks:
					refName = fk.referencedTable().getSymbolName(True)
					colName = ":" + fk.getFirstColumn().getName()
					func.add(SCFunc("add_foreign_key", tableName, refName, "column: " + colName))
		
		if (self.resolved):
			self.add(cls)


###############################################################################
#
# The class that acutally does the exporting
#
###############################################################################
class Exporter:
	def __init__(self, catalog):
		self.migNum = 0
		self.tables = Tables(catalog)
		self.sortedTables = self.tables.topSort().linkedList

		if self.choosePath():
			self.writeMigrations()
			mforms.Utilities.show_message(
				"Export Successful",
				"The migration files were successfully created and placed in the folder you selected.",
				'OK', "", "")

	def choosePath(self):
		file_chooser = mforms.newFileChooser(None, mforms.OpenDirectory)
		if file_chooser.run_modal() == mforms.ResultOk:
		    self.path = file_chooser.get_path()
		    return True
		return False

	def genMigrationFileName(self, name):
		tblName = inflection.pluralize(inflection.underscore(name))
		now = datetime.datetime.now()
		fileName = '/%s%s%s%s_%s.rb' % (now.strftime('%Y'), now.strftime('%m'), now.strftime('%d'), str(self.migNum).zfill(6), tblName)
		self.migNum += 1
		return fileName

	def writeMigrations(self):
		for table in self.sortedTables:
			self.writeMigration(table)

		self.writeResolved()

	def writeMigration(self, table):
		fileName = self.genMigrationFileName("Create_" + table.getName())
		f = MigrationFile(table)
		self.writeFile(self.path + fileName, f)

	def writeResolved(self):
		fileName = self.genMigrationFileName("AddResolvedForeignKeys")

		f = ResolvedFile(self.sortedTables)
		if (f.resolved):
			self.writeFile(self.path + fileName, f)

	def writeFile(self, path, sc):
		try:
			with open(path, 'w+') as f:
				# Write to the file
				sc.write(f)
		except IOError as e:
			mforms.Utilities.show_error(
			'Save to File',
			'Could not save to file "%s": %s' % (self.path, str(e)),
			'OK')

# generateRailsMigration(grt.root.wb.doc.physicalModels[0].catalog)
