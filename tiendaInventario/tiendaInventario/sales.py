from errors import (
    InsufficientStockError,
    ProductNotFoundError,
    SimulatedFailureError,
    ValidationError,
)


def registerSale(connection, idProducto, cantidad, simulateFailure=False):
    if cantidad <= 0:
        raise ValidationError("La cantidad vendida debe ser mayor que cero")
    try:
        connection.execute("BEGIN IMMEDIATE")
        producto = connection.execute(
            "SELECT idProducto, nombre, precio, cantidadDisponible FROM productos WHERE idProducto = ?",
            (idProducto,),
        ).fetchone()
        if producto is None:
            raise ProductNotFoundError(f"No existe un producto con id {idProducto}")
        if producto["cantidadDisponible"] < cantidad:
            raise InsufficientStockError(
                f"Stock insuficiente: disponible {producto['cantidadDisponible']}, solicitado {cantidad}"
            )
        precioUnitario = producto["precio"]
        total = precioUnitario * cantidad
        cursor = connection.execute(
            "INSERT INTO ventas (idProducto, cantidad, precioUnitario, total) VALUES (?, ?, ?, ?)",
            (idProducto, cantidad, precioUnitario, total),
        )
        if simulateFailure:
            raise SimulatedFailureError(
                "Error controlado despues de registrar la venta y antes de actualizar el inventario"
            )
        connection.execute(
            "UPDATE productos SET cantidadDisponible = cantidadDisponible - ? WHERE idProducto = ?",
            (cantidad, idProducto),
        )
        connection.commit()
        return cursor.lastrowid
    except Exception:
        connection.rollback()
        raise


def listSales(connection):
    return connection.execute(
        """
        SELECT v.idVenta, p.nombre, v.cantidad, v.precioUnitario, v.total, v.fechaVenta
        FROM ventas v
        INNER JOIN productos p ON p.idProducto = v.idProducto
        ORDER BY v.idVenta
        """
    ).fetchall()


def countSales(connection):
    return connection.execute("SELECT COUNT(*) FROM ventas").fetchone()[0]
