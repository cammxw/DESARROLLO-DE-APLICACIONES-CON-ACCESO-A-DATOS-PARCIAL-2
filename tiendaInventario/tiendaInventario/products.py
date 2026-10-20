import sqlite3

from errors import ProductInUseError, ProductNotFoundError, ValidationError


def validateName(nombre):
    if nombre is None or not str(nombre).strip():
        raise ValidationError("El nombre no puede estar vacio")


def validatePrice(precio):
    if precio < 0:
        raise ValidationError("El precio no puede ser negativo")


def validateStock(cantidad):
    if cantidad < 0:
        raise ValidationError("La cantidad no puede ser negativa")


def addProduct(connection, nombre, precio, cantidad):
    validateName(nombre)
    validatePrice(precio)
    validateStock(cantidad)
    try:
        cursor = connection.execute(
            "INSERT INTO productos (nombre, precio, cantidadDisponible) VALUES (?, ?, ?)",
            (nombre.strip(), precio, cantidad),
        )
        connection.commit()
    except sqlite3.IntegrityError:
        connection.rollback()
        raise ValidationError("Ya existe un producto con ese nombre")
    return cursor.lastrowid


def listProducts(connection):
    return connection.execute(
        "SELECT idProducto, nombre, precio, cantidadDisponible FROM productos ORDER BY idProducto"
    ).fetchall()


def getProduct(connection, idProducto):
    return connection.execute(
        "SELECT idProducto, nombre, precio, cantidadDisponible FROM productos WHERE idProducto = ?",
        (idProducto,),
    ).fetchone()


def requireProduct(connection, idProducto):
    producto = getProduct(connection, idProducto)
    if producto is None:
        raise ProductNotFoundError(f"No existe un producto con id {idProducto}")
    return producto


def updatePrice(connection, idProducto, precio):
    validatePrice(precio)
    requireProduct(connection, idProducto)
    connection.execute(
        "UPDATE productos SET precio = ? WHERE idProducto = ?",
        (precio, idProducto),
    )
    connection.commit()


def updateStock(connection, idProducto, cantidad):
    validateStock(cantidad)
    requireProduct(connection, idProducto)
    connection.execute(
        "UPDATE productos SET cantidadDisponible = ? WHERE idProducto = ?",
        (cantidad, idProducto),
    )
    connection.commit()


def deleteProduct(connection, idProducto):
    requireProduct(connection, idProducto)
    totalVentas = connection.execute(
        "SELECT COUNT(*) FROM ventas WHERE idProducto = ?",
        (idProducto,),
    ).fetchone()[0]
    if totalVentas > 0:
        raise ProductInUseError(
            f"El producto tiene {totalVentas} venta(s) registradas y no puede eliminarse"
        )
    try:
        connection.execute("DELETE FROM productos WHERE idProducto = ?", (idProducto,))
        connection.commit()
    except sqlite3.IntegrityError:
        connection.rollback()
        raise ProductInUseError("El producto esta referenciado por otras tablas")
