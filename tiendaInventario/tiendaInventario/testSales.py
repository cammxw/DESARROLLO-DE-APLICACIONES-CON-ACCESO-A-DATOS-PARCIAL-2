import unittest

from database import createTables, getConnection
from errors import (
    InsufficientStockError,
    ProductInUseError,
    ProductNotFoundError,
    SimulatedFailureError,
    ValidationError,
)
import products
import sales


class ShopTestCase(unittest.TestCase):
    def setUp(self):
        self.connection = getConnection(":memory:")
        createTables(self.connection)
        self.idProducto = products.addProduct(self.connection, "Arduino Uno", 85000.0, 10)

    def tearDown(self):
        self.connection.close()

    def stock(self):
        return products.getProduct(self.connection, self.idProducto)["cantidadDisponible"]

    def testSuccessfulSaleUpdatesInventory(self):
        idVenta = sales.registerSale(self.connection, self.idProducto, 4)
        self.assertEqual(idVenta, 1)
        self.assertEqual(self.stock(), 6)
        self.assertEqual(sales.countSales(self.connection), 1)

    def testSaleWithUnknownProduct(self):
        with self.assertRaises(ProductNotFoundError):
            sales.registerSale(self.connection, 999, 1)
        self.assertEqual(sales.countSales(self.connection), 0)

    def testSaleWithInsufficientStock(self):
        with self.assertRaises(InsufficientStockError):
            sales.registerSale(self.connection, self.idProducto, 11)
        self.assertEqual(self.stock(), 10)
        self.assertEqual(sales.countSales(self.connection), 0)

    def testSaleWithInvalidQuantity(self):
        with self.assertRaises(ValidationError):
            sales.registerSale(self.connection, self.idProducto, 0)

    def testRollbackKeepsDataIntact(self):
        with self.assertRaises(SimulatedFailureError):
            sales.registerSale(self.connection, self.idProducto, 3, simulateFailure=True)
        self.assertEqual(self.stock(), 10)
        self.assertEqual(sales.countSales(self.connection), 0)
        self.assertFalse(self.connection.in_transaction)

    def testSaleAfterRollbackStillWorks(self):
        with self.assertRaises(SimulatedFailureError):
            sales.registerSale(self.connection, self.idProducto, 3, simulateFailure=True)
        sales.registerSale(self.connection, self.idProducto, 3)
        self.assertEqual(self.stock(), 7)
        self.assertEqual(sales.countSales(self.connection), 1)

    def testDeleteProductWithSalesIsRejected(self):
        sales.registerSale(self.connection, self.idProducto, 1)
        with self.assertRaises(ProductInUseError):
            products.deleteProduct(self.connection, self.idProducto)
        self.assertIsNotNone(products.getProduct(self.connection, self.idProducto))

    def testDeleteProductWithoutSales(self):
        products.deleteProduct(self.connection, self.idProducto)
        self.assertIsNone(products.getProduct(self.connection, self.idProducto))

    def testSalesHistoryUsesJoin(self):
        sales.registerSale(self.connection, self.idProducto, 2)
        rows = sales.listSales(self.connection)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["nombre"], "Arduino Uno")
        self.assertEqual(rows[0]["total"], 170000.0)

    def testDuplicateNameIsRejected(self):
        with self.assertRaises(ValidationError):
            products.addProduct(self.connection, "Arduino Uno", 1.0, 1)


if __name__ == "__main__":
    unittest.main()
