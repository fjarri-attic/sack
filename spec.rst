==================================
Project Sack design specifications
==================================

-----------
Preferences
-----------

* Object dragging:
  * Left button drag sets association, right button drag moves object (i.e., to shelf)
  * Right button drag sets association, left button drag moves object

  Default should be the second option: left button dragging is usually associated with moving
  something.

* Double click opens object in: new tab, current tab

* Show hidden fields: yes or no, no by default.
  Probably leading underscore should not be shown; other color should be used instead.

* Color and fonts scheme:
  * Main text style
  * Hidden field names
  * Object title (text on object control)

* Editing mode (autocommit, manual commit)

----------------
Object structure
----------------

Object field names can contain only letters, numbers, underscores and hyphens.
Root field should be a dictionary. Field names should start either from underscore or a letter.
Field names starting from underscore are considered hidden (will be shown only when corresponding
setting is enabled).

Hidden fields, undeleteable:
  * ``_Title`` (string; taken from display class's ``TitleTemplate`` if empty)
  * ``_Tags`` (points to list)
  * ``_DisplayClass`` (points to display class object; can be None only for root object;
    by default the corresponding default class from root object is used)
  * ``_Associations`` (points to list of object references)

Display class objects
---------------------

Display class objects define how objects are displayed. They have the following fields:
  * ``TitleTemplate``: string, defining how title is composed
  * ``FieldsOrder``: nested lists, defining the order of fields on main window view;
    other fields are shown alphabetically.

Builtins
--------

Database initially contains the single root object, whose _DisplayClass equals to None.
It is a root object and it serves as a starting point when accessing the database. Full specification:

* ``_Title``: None
* ``_Tags``: None
* ``_DisplayClass``: None
* ``DisplayClasses``:
  * ``DisplayClass``: points to built-in display class object
  * ``Tag``: points to built-in tag class
  * ``Default``: points to built-in default display class

Built-in display classes
------------------------

Each Display class's ``_DisplayClass`` field points to the metaclass with the following contents:

* ``_DisplayClass``: points to self
* ``Title``: "Display class for display classes"
* ``TitleTemplate``: "$Title"
* ``FieldsOrder``:
  - "Title"
  - "TitleTemplate"
  - "FieldsOrder"

Display class for tags:

* ``Title``: "Display class for tags"
* ``TitleTemplate``: "$Title"
* ``FieldsOrder``:
  - "Title"
  - "Description"

Default display class:

* ``Title``: "Default display class"
* ``TitleTemplate``: "$Title"
* ``FieldsOrder``:
  - "Title"
  - "Data"

Title template
--------------

A string, containing pointers to object's fields prefixed by dollar signs. The value of the field
is inserted in place of each reference during display. Reference to object is resolved as the title
of this object (objects are memoized, so cyclic references are avoided).

Example: "$Artist - $Album - $Title".

--------------
User Interface
--------------

Menu bar + window per each opened database.
Currently windows cannot interconnect (like moving objects from one DB to another).

**FUTURE**: allow DB windows interconnection.

Object control
--------------

Object is represented by a custom control (at least, a label with colored border).
On diagrams it is shown as ``/Object/``.

Label text is taken from object's ``_Title`` field. Object has di

Context menu items for each object control:
* Copy as YAML (or other registered exporters)
* Open in new tab
* Open in current tab
* Move to shelf
* Delete
* Add to associations of current object (if applicable)
* Delete from associations of current object (if applicable)

Each object can be dragged with left or right key pressed.
Double click on an object control opens it in a tab.

DB window
---------

____________________________________
| Database name                    |
|-----------------------------------
| Tag panel | Main window | Shelf  |
|           |             |        |
|___________|_____________|________|

Tag panel and shelf are hideable.

Tag panel
---------

_________________
| [ ] /Tag1/  |A|
| [ ] /Tag2/  |#|
| [ ] /Tag3/  |#|
| [ ] /Tag4/  | |
|             | |
|             | |
|             | |
|_____________|V|

Panel is filled with all objects whose ``_DisplayClass`` points to tag display class.
The result of marking and unmarking tags depends on main windows contents. If main window is in
object view mode, the result is setting/unsetting tags to/from object. If main window is in
search mode, the result is filtering search results.

Shelf
-----

_________________
| /Object1/   |A|
| /Object2/   |#|
| /Object3/   | |
|             | |
|_____________|V|


Main window
___________

Main window is a tabbed control. Each tab can be in one of two states:
object view and search.

________________________
|/ Title1 \/_____\_____|
|                      |
|______________________|
| Status bar           |
------------------------

Title of the tab is an object title (the beginning of it, if the title is too long) or
"Search" for search mode.

New tabs are opened in search mode by default (by clicking on an empty space or
on a special "new tab" button).

Object view
~~~~~~~~~~~

________________________________________
| Title                    | /Object1/ |
|--------------------------- /Object2/ |
| - Key1: Value1           |           |
| - Key2:                  |           |
|   Subkey1: Value         |           |
| - Key3:                  |           |
|   - (2 elements)         |           |
|     - val1               |           |
|     - val2               |           |
|   - List value 2         |           |
| Key4: /Object ref/       |           |
----------------------------------------

Right column contain objects from hidden ``_Associations`` field.

Key names have separate styles.

Right click on a title shows context menu ("Copy title", "Copy as", "Create key").

Right click on key name (or on plus/minus sign) shows context menu: "Copy as" (submenu with list of
possible exporters + copy full key name), "Delete", "Collapse/Unfold". Additionally, for a key: "Add new key",
for a list: "Insert new element to the beginning", "Insert new element to the end". For a plus/minus
sign pointing to the element of the list: "Insert new element before", "Insert new element after".
New elements/keys are created with the value of NULL. Left click on plus/minus sign unfolds/collapses
the list or dictionary.

Left click on value allows to edit it. Dragging object on a value sets a value to the reference to
this object. Right click on value shows context menu: "Copy", "Paste" (submenu with list of possible
importers), "Set to NULL", "Set to dictionary", "Set to list". If pasting as a data (YAML, XML, so on),
necessary structures are created.

Search mode
~~~~~~~~~~~

____________________________
| /Object1/              |A|
| /Object2/              | |
|                        |V|
|---------------------------
| Search condition here    |
|__________________________|

Search condition edit control expands according to condition size (until a half of area height).

When user enters a condition and hits enter, it gets parsed and if there are errors, they
get underlined in edit control and error in status line is shown.

Menu
____

File -> New tab, Open, Commit
Edit -> Rollback (for manual commit mode), Open search tab
Tools -> Repair

-----------------------
Search condition syntax
-----------------------

Simple condition: <field name> <comparison> <value>. Value is integer, float, "NULL" (case-insensitive)
or string (without spaces or enclosed in double quotes with escaped double quotes and backslashes inside).
Comparison is one of the symbols =, ~, <, >, <=, >=.

Compound condition: <condition> <operator> <condition>. Condition is a simple condition, enclosed in
parenthesis. Operator is "AND" or "OR" (case-insensitive).
