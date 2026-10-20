import sqlite3

defaultDatabaseName = "tienda.db"

schemaScript = """
CREATE TABLE IF NOT EXISTS productos (
    idProducto INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL UNIQUE,
    precio REAL NOT NULL CHECK (precio >= 0),
    cantidadDisponible INTEGER NOT NULL CHECK (cantidadDisponible >= 0)
);

CREATE TABLE IF NOT EXISTS ventas (
    idVenta INTEGER PRIMARY KEY AUTOINCREMENT,
    idProducto INTEGER NOT NULL,
    cantidad INTEGER NOT NULL CHECK (cantidad > 0),
    precioUnitario REAL NOT NULL,
    total REAL NOT NULL,
    fechaVenta TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (idProducto) REFERENCES productos (idProducto) ON DELETE RESTRICT
);
"""


def getConnection(databaseName=defaultDatabaseName):
    connection = sqlite3.connect(databaseName)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def createTables(connection):
    connection.executescript(schemaScript)
    connection.commit()
