""" Set constants for manual run """

# which apps to include
# APP_LABELS = ["okr", "admin"]
APP_LABELS = ["okr"]

# HTML above generated tables
HTML_TOP = """
<!doctype html>

<html lang="de">
<head>
<meta charset="utf-8">

<title>Datenbank-Tabellen WDR OKR</title>

<style>
body {
  font-family: Arial, Helvetica, sans-serif;
}

h3 {
  background-color: #00345e;
  color: white;
  padding: 10px;
  margin-top: 80px;
}

.docstring {
  margin-bottom: 15px;
}

table {
  width: 100%;
  border-collapse: collapse;
}

td {
  border: 1px solid black;
  padding: 5px;
  width: 20%;
}

th {
  border: 1px solid black;
  background-color: grey;
  padding: 6px;
}

tr:nth-child(even) {
  background-color: #f2f2f2;
}
tr:hover {
  background-color: rgb(216, 216, 216);
}

</style>

</head>

<body>

<div id="main">
"""

# HTML below generated table
HTML_BOTTOM = """
</div>

</body>
</html>
"""

# set name for completed html file
FILENAME = "database.html"
