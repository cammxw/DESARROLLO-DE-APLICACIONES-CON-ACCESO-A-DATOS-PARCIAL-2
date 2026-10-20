from database import createTables, getConnection
from demoRollback import runRollbackDemo
from errors import ShopError
import products
import sales


def readText(message):
    while True:
        value = input(message).strip()
        if value:
            return value
        print("El valor no puede estar vacio")


def readInt(message):
    while True:
        try:
            return int(input(message).strip())
        except ValueError:
            print("Ingrese un numero entero valido")


def readFloat(message):
    while True:
        try:
            return float(input(message).strip().replace(",", "."))
        except ValueError:
            print("Ingrese un numero valido")


def printProducts(rows):
    if not rows:
        print("No hay productos registrados")
        return
    print(f"{'ID':<5}{'Nombre':<30}{'Precio':>12}{'Disponible':>12}")
    print("-" * 59)
    for row in rows:
        print(
            f"{row['idProducto']:<5}{row['nombre']:<30}"
            f"{row['precio']:>12.2f}{row['cantidadDisponible']:>12}"
        )


def printSales(rows):
    if not rows:
        print("No hay ventas registradas")
        return
    print(f"{'Venta':<7}{'Producto':<28}{'Cant.':>6}{'P. unit.':>11}{'Total':>12}  Fecha")
    print("-" * 80)
    for row in rows:
        print(
            f"{row['idVenta']:<7}{row['nombre']:<28}{row['cantidad']:>6}"
            f"{row['precioUnitario']:>11.2f}{row['total']:>12.2f}  {row['fechaVenta']}"
        )


def addProductOption(connection):
    nombre = readText("Nombre: ")
    precio = readFloat("Precio: ")
    cantidad = readInt("Cantidad disponible: ")
    idProducto = products.addProduct(connection, nombre, precio, cantidad)
    print(f"Producto registrado con id {idProducto}")


def listProductsOption(connection):
    printProducts(products.listProducts(connection))


def updatePriceOption(connection):
    idProducto = readInt("Id del producto: ")
    precio = readFloat("Nuevo precio: ")
    products.updatePrice(connection, idProducto, precio)
    print("Precio actualizado")


def updateStockOption(connection):
    idProducto = readInt("Id del producto: ")
    cantidad = readInt("Nueva cantidad disponible: ")
    products.updateStock(connection, idProducto, cantidad)
    print("Cantidad actualizada")


def deleteProductOption(connection):
    idProducto = readInt("Id del producto a eliminar: ")
    products.deleteProduct(connection, idProducto)
    print("Producto eliminado")


def registerSaleOption(connection):
    idProducto = readInt("Id del producto: ")
    cantidad = readInt("Cantidad a vender: ")
    idVenta = sales.registerSale(connection, idProducto, cantidad)
    print(f"Venta {idVenta} registrada y inventario actualizado")


def listSalesOption(connection):
    printSales(sales.listSales(connection))


def rollbackDemoOption(connection):
    idProducto = readInt("Id del producto para la prueba: ")
    cantidad = readInt("Cantidad a vender en la prueba: ")
    runRollbackDemo(connection, idProducto, cantidad)


menuOptions = {
    "1": ("Registrar producto", addProductOption),
    "2": ("Consultar productos", listProductsOption),
    "3": ("Actualizar precio", updatePriceOption),
    "4": ("Actualizar cantidad", updateStockOption),
    "5": ("Eliminar producto", deleteProductOption),
    "6": ("Registrar venta", registerSaleOption),
    "7": ("Historial de ventas", listSalesOption),
    "8": ("Demostrar rollback con error controlado", rollbackDemoOption),
    "0": ("Salir", None),
}


def printMenu():
    print()
    print("=== TIENDA DE COMPONENTES ELECTRONICOS ===")
    for key, (label, _) in menuOptions.items():
        print(f"{key}. {label}")


def main():
    connection = getConnection()
    createTables(connection)
    try:
        while True:
            printMenu()
            try:
                choice = input("Seleccione una opcion: ").strip()
            except EOFError:
                break
            if choice == "0":
                break
            option = menuOptions.get(choice)
            if option is None:
                print("Opcion no valida")
                continue
            try:
                option[1](connection)
            except ShopError as error:
                print(f"Error: {error}")
    finally:
        connection.close()
    print("Hasta pronto")


if __name__ == "__main__":
    main()
