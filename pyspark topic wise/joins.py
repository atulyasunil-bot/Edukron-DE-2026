import os
import sys

os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

from pyspark.sql import SparkSession
import pyspark.sql.functions as F

spark = (
    SparkSession.builder
    .appName("Assignment08_Joins")
    .master("local[2]")
    .getOrCreate()
)

# Sample customers dataset
customers_data = [
    (1, "Aarav", "Sharma"),
    (2, "Meera", "Patel"),
    (3, "Rohan", "Verma"),
    (4, "Priya", "Nair"),
]
customers = spark.createDataFrame(customers_data, ["customer_id", "first_name", "last_name"])

# Sample orders dataset
orders_data = [
    (101, 1, 1500.0, "2025-01-10", "Completed"),
    (102, 1, 2500.0, "2025-02-15", "Completed"),
    (103, 2,  800.0, "2025-03-01", "Completed"),
    (104, 5,  450.0, "2025-03-12", "Pending"),
]
orders = spark.createDataFrame(orders_data, ["order_id", "customer_id", "total_amount", "order_date", "order_status"])

# Sample products dataset
products_data = [
    (501, "Laptop", "Electronics"),
    (502, "Mouse", "Electronics"),
    (503, "Desk Lamp", "Home"),
    (504, "Water Bottle", "Fitness"),
]
products = spark.createDataFrame(products_data, ["product_id", "product_name", "category"])

# Sample order items dataset
order_items_data = [
    (101, 501, 1, 1500.0),
    (102, 501, 1, 2000.0),
    (102, 502, 2,  500.0),
    (103, 502, 1,  800.0),
]
order_items = spark.createDataFrame(order_items_data, ["order_id", "product_id", "quantity", "item_amount"])

# Sample payments dataset with order link
payments_data = [
    (901, 101, "UPI", "Success"),
    (902, 102, "Card", "Success"),
    (903, 999, "NetBanking", "Failed"),
]
payments = spark.createDataFrame(payments_data, ["payment_id", "order_id", "payment_type", "payment_status"])

# Sample stores dataset
stores_data = [
    (1, "Indiranagar Flagship", "Karnataka"),
    (2, "Koramangala Hub", "Karnataka"),
    (3, "Bandra Central", "Maharashtra"),
    (4, "Andheri West", "Maharashtra"),
]
stores = spark.createDataFrame(stores_data, ["store_id", "store_name", "state"])

# Inner join: orders with customers
inner = orders.join(customers, "customer_id", "inner")
inner.show()

# Left outer join: all customers with matching orders
left = customers.join(orders, "customer_id", "left")
left.show()

# Right outer join: all orders with matching customers
right = customers.join(orders, "customer_id", "right")
right.show()

# Full outer join: all records from both datasets
full_outer = customers.join(orders, "customer_id", "outer")
full_outer.show()

# Left semi join: customers who placed at least one order
left_semi = customers.join(orders, "customer_id", "left_semi")
left_semi.show()

# Left anti join: customers who never placed an order
left_anti = customers.join(orders, "customer_id", "left_anti")
left_anti.show()

# Cross join: cartesian product of customers and products
cross = customers.limit(2).crossJoin(products.limit(2))
cross.select("customer_id", "product_id").show()

# Self join: pairs of orders placed by the same customer
o1 = orders.alias("o1")
o2 = orders.alias("o2")
self_join = (
    o1.join(
        o2,
        (F.col("o1.customer_id") == F.col("o2.customer_id")) &
        (F.col("o1.order_id") < F.col("o2.order_id"))
    )
    .select(
        F.col("o1.customer_id"),
        F.col("o1.order_id").alias("order_id_a"),
        F.col("o2.order_id").alias("order_id_b"),
        F.col("o1.total_amount").alias("amount_a"),
        F.col("o2.total_amount").alias("amount_b")
    )
)
self_join.show()

# Products that were never sold using left anti join
sold_products = order_items.select("product_id").distinct()
never_sold = products.join(sold_products, "product_id", "left_anti")
never_sold.show()

# Orders without payment records
orders_without_payment = orders.join(payments, "order_id", "left_anti")
orders_without_payment.show()

# Customers with successful payments
successful_payments = payments.filter(F.col("payment_status") == "Success")
customers_with_success = (
    customers
    .join(orders.join(successful_payments, "order_id"), "customer_id", "left_semi")
)
customers_with_success.show()

# Self join on stores sharing the same state
s1 = stores.alias("s1")
s2 = stores.alias("s2")
same_state_stores = (
    s1.join(
        s2,
        (F.col("s1.state") == F.col("s2.state")) &
        (F.col("s1.store_id") < F.col("s2.store_id"))
    )
    .select(
        F.col("s1.store_name").alias("store_a"),
        F.col("s2.store_name").alias("store_b"),
        F.col("s1.state")
    )
)
same_state_stores.show()

# Multi table join: orders, order items, and products
order_product = (
    orders
    .join(order_items, "order_id")
    .join(products, "product_id")
    .select(
        "order_id", "customer_id", "order_date", "order_status",
        "product_id", "product_name", "category", "quantity", "item_amount"
    )
)
order_product.show()

spark.stop()