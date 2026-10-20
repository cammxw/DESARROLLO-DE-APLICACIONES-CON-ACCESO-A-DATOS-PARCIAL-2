from database import createTables, getConnection
from errors import SimulatedFailureError
from products import addProduct, requireProduct
from sales import countSales, registerSale


def runRollbackDemo(connection, idProducto, cantidad, output=print):
    stockAntes = requireProduct(connection, idProducto)["cantidadDisponible"]
    ventasAntes = countSales(connection)
    output(f"Antes   -> stock: {stockAntes} | ventas registradas: {ventasAntes}")
    output(f"Intentando vender {cantidad} unidad(es) con falla simulada...")
    try:
        registerSale(connection, idProducto, cantidad, simulateFailure=True)
    except SimulatedFailureError as error:
        output(f"Error capturado: {error}")
        output("Se ejecuto rollback() sobre toda la operacion")
    stockDespues = requireProduct(connection, idProducto)["cantidadDisponible"]
    ventasDespues = countSales(connection)
    output(f"Despues -> stock: {stockDespues} | ventas registradas: {ventasDespues}")
    intact = stockAntes == stockDespues and ventasAntes == ventasDespues
    output("Resultado: datos intactos" if intact else "Resultado: INCONSISTENCIA")
    return intact


if __name__ == "__main__":
    connection = getConnection(":memory:")
    createTables(connection)
    idProducto = addProduct(connection, "Resistencia 10k", 120.0, 50)
    runRollbackDemo(connection, idProducto, 5)
    connection.close()
