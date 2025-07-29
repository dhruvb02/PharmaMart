# Admin Password = secure@255_254
import mysql.connector
import string
import random
from datetime import date, datetime

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="root"
)

mycursor = mydb.cursor()

mycursor.execute("use pharmamart")

def login(option):
  while(True):
    username = input("Enter Username: ")
    password = input("Enter Password: ")

    query_list = list()
    query_list.append("Select * from credentials C join customer WHERE C.username = '" +username+ "' AND C.passwd = '" + password + "'") 
    query_list.append("Select * from credentials C join seller WHERE C.username = '" +username+ "' AND C.passwd = '" + password + "'") 
    query_list.append("Select * from credentials C join admin WHERE C.username = '" +username+ "' AND C.passwd = '" + password + "'") 

    quer_cred = query_list[option-1]
    mycursor.execute(quer_cred)
    rows_cred = mycursor.fetchall()
    if (len(rows_cred) == 0):
      print("Username or Password Incorrect!\n\nPress 1 to try again or 2 to go Back")
      o = int(input())

      if (o==2):
        break
      if (o==1):
        continue

    else:
      print("\nWelcome back " + username + "!\n")
      table = ""
      ID = ""
      if (option==1):
        table = "customer"
        ID = "customer_ID"
      elif(option==2):
        table = "seller"
        ID = "seller_id"
      elif (option==3):
        table = "admin"
        ID = "admin_ID"

      mycursor.execute("Select {} from {} where username = '{}'".format(ID, table, username))
      
      row = mycursor.fetchone()
      return [option, row[0]]
    
  return 0

def register(option):
  while(True):
    username = input("Enter Username: ")
    password = input("Enter Password: ")

    query_cred = "Select * from credentials WHERE username = '" +username+ "'"
    mycursor.execute(query_cred)
    rows_cred = mycursor.fetchall()

    # IF no entry with entered username exists, Register the user
    if (len(rows_cred) == 0):
      q_reg = "INSERT INTO credentials VALUES ('" + username + "', '" + password + "')"
      mycursor.execute(q_reg)
      
      if(option==1):
        customer_details(username)
      elif(option==2):
        seller_details(username)
      elif(option==3):
        admin_details(username)

      break

    # IF username already exists, ask to enter another username or Go back
    else:
      print("Username already taken, press 1 to enter another username or press 2 to go back!\n")
      o = int(input())
      if (o==1):
        continue
      if (o==2):
        break

def customer_details(username):
  
    mycursor.execute("SELECT MAX(customer_id) FROM customer")
    result = mycursor.fetchone()    
    customer_id = result[0] + 1 if result[0] else 1

    first_name = input("Enter first name: ")
    middle_name = input("Enter middle name: ")
    last_name = input("Enter last name: ")
    address_house_no = input("Enter house number and address: ")
    dob = input("Enter date of birth (yyyy-mm-dd): ")
    phone_number = int(input("Enter phone number: "))
    email = input("Enter email: ")

    sql = f"INSERT INTO customer VALUES ({customer_id}, '{first_name}', '{middle_name}', '{last_name}', '{address_house_no}', '{dob}', {phone_number}, '{email}', '{username}')"
    sql2 = f"INSERT INTO pharmamart_account VALUES ({customer_id}, {customer_id}, 0)"
    mycursor.execute(sql)
    mycursor.execute(sql2)

    print("Welcome {}! You have successfully registered to Pharmamart!\n\n".format(first_name))

def seller_details(username):
  mycursor.execute("SELECT MAX(seller_id) FROM seller")
  result = mycursor.fetchone()

  seller_id = result[0] + 1 if result[0] else 1
  name = input("Enter seller name: ")
  address = input("Enter seller address: ")
  phone = int(input("Enter seller phone number: "))
  email = input("Enter seller email: ")

  sql = f"INSERT INTO seller VALUES ({seller_id}, '{name}', '{address}', {phone}, '{email}', 0, '{username}')"
  mycursor.execute(sql)
  print("Welcome {}! You have successfully registered to Pharmamart!\n\n".format(name))

def admin_details(username):
  mycursor.execute("SELECT MAX(admin_id) FROM admin")
  result = mycursor.fetchone()

  admin_id = result[0] + 1 if result[0] else 1
  name = input("Enter admin name: ")
  phone = int(input("Enter admin phone number: "))
  email = input("Enter seller email: ")

  sql = f"INSERT INTO admin Values ({admin_id}, '{name}', {phone}, '{email}', '{username}')"
  mycursor.execute(sql)
  print("Welcome {}! You have successfully registered to Pharmamart!\n\n".format(name))

def checkout(products, total_price, customer_id):
  # print("Products in Cart: \n\n")
  # print("PRODUCT\t\tQuantity")
  pid = 0

  for product in products:
    mycursor.execute(f"SELECT product_name FROM product WHERE product_id = {product[0]}")
    product_name = mycursor.fetchone()[0]
    quer = f"Select * from product WHERE product_id = {product[0]} AND Prescription_Required = '1' "
    mycursor.execute(quer)
    rows_cred = mycursor.fetchall()

    if (len(rows_cred) != 0):
      mycursor.execute(f"SELECT FirstName, MiddleName, LastName FROM customer WHERE customer_id = {customer_id}")
      result = mycursor.fetchone()

      mycursor.execute(f"SELECT DOB FROM customer WHERE customer_id ={customer_id}")
      result2 = mycursor.fetchone()
      dob = result2[0]
      today = date.today()
      age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
      
      out = prescription(result[0], result[1], result[2], age)

      if (out==0):
        return
      else:
        pid = out
        
    print("{}\t\t{}".format(product_name, product[1]))

  print("\n\n1. Place Order\n2. Cancel and go back")

  op = int(input())
   
  if (op==2):
    Home(customer_id)
  
  op1 = 4
  while(True):
    op1 = int(input("\nSelect mode of Payment:\n1. Wallet\n2. UPI\n3. COD\n4. Cancel and Go back\nChoose option: "))

    if (op1==1):
      mycursor.execute(f"SELECT wallet_balance FROM pharmamart_account WHERE customer_id = {customer_id}")
      result = mycursor.fetchone()
      if result and result[0] < total_price:
        print("Wallet doesn't have sufficient balance!\n\nChoose another mode of payment!\n")
        continue
      break
      
    if (op1==4):
      break
    
    if (op1==2):
      print("Payment of " + str(total_price) + " confirmed using UPI\n")
      if (total_price>2000):
        print("Congratulations! Cashback of 200 has been credited to your account wallet!\n")
      break
    print()
  if (op1==4):
    Home(customer_id)

  mycursor.execute("SELECT MAX(order_id) FROM _order")
  result = mycursor.fetchone()
  o_id = result[0] + 1 if result[0] else 1

  format = "track.gg/{}{}{}{}{}{}"
    
  first_two = ''.join(random.choices(string.ascii_lowercase, k=2))
  three_numbers = ''.join(random.choices(string.digits, k=3))
  two_letters = ''.join(random.choices(string.ascii_uppercase, k=2))
  two_numbers = ''.join(random.choices(string.digits, k=2))
  final_letters = ''.join(random.choices(string.ascii_lowercase, k=2))

  fake_link = format.format(first_two, three_numbers, two_letters, two_numbers, final_letters, two_numbers)

  today = datetime.today()
  today = str(today.strftime('%Y-%m-%d'))

  mycursor.execute("SELECT DISTINCT shipping_agent FROM _order")
  shipping_agents = mycursor.fetchall()
  sa = random.choice(shipping_agents)[0]

  q_order = f"INSERT INTO _order VALUES ({o_id}, {total_price}, '{today}', '{sa}', '{fake_link}')"
  mycursor.execute(q_order)

  query_ = f"SELECT Account_ID FROM pharmamart_account WHERE customer_ID = {customer_id}"
  mycursor.execute(query_)
  result = mycursor.fetchone()
  account_ID = result[0]

  mycursor.execute(f"INSERT INTO my_prescription VALUES({pid}, {customer_id}, {account_ID}, {o_id})")


  for product in products:
    mycursor.execute(f"SELECT seller_id FROM sells WHERE product_id = {product[0]} AND quantity >= {product[1]}")

    seller_id = mycursor.fetchone()[0]
    mycursor.execute(f"INSERT INTO _contains (order_id, product_id, seller_id, quantity) VALUES ({o_id}, {product[0]}, {seller_id}, {product[1]})")
    
    mycursor.execute(f"INSERT INTO my_orders VALUES ({o_id}, {seller_id}, {customer_id}, {account_ID}, 'Order Placed')")


  print("\nOrder placed! (Order ID: {}) \n".format(o_id))
  mydb.commit()
  Home(customer_id)

def prescription(fname, mname, lname, age):
  option = int(input("A product in your order requires a prescription\n\n1. Upload Prescription \n2. Cancel Order \n\nChoose option: "))

  if (option==2):
    return 0
  
  elif (option==1):
    dname1 = input("Enter Doctor's First name: ")
    dname2 = input("Enter Doctor's Middle name: ")
    dname3 = input("Enter Doctor's Last name: ")

    mycursor.execute("SELECT MAX(prescription_id) FROM prescription")
    result = mycursor.fetchone()

    p_id = result[0] + 1 if result[0] else 1
    mycursor.execute("INSERT INTO prescription VALUES ({}, '{}', '{}', '{}', {},'{}', '{}', '{}', 0, NULL)".format(p_id, fname, mname, lname, age, dname1, dname2, dname3))

    return p_id
  else:
    "Choose a valid option"
    return prescription(fname, mname, lname, age)

def seller_page(seller_id):

  while (True):
    o = int(input("\n1. Add a new Product \n2. Update Quantity of a Product \n3. Sign out\n\nChoose option: "))

    if (o==1):
      mycursor.execute("SELECT MAX(product_id) FROM product")
      result = mycursor.fetchone()

      product_id = result[0] + 1 if result[0] else 1

      product_name = input("Enter the product name: ")
      product_price = int(input("Enter the product price: "))
      product_category = input("Enter the product category: ")
      prescription_required = input("Is prescription required for this product? (1 for Yes, 0 for No): ")
      expiry_date = input("Enter the expiry date (YYYY-MM-DD): ")
      discount = int(input("Enter the discount percentage: "))
      quantity = int(input("Enter quantity of product: "))
      sql = "INSERT INTO product (Product_ID, Product_Name, Product_Price, Product_Category, Prescription_Required, Expiry_Date, Discount, Deal_ProductID) VALUES ({}, '{}', {}, '{}', '{}', '{}', {}, NULL)"
      mycursor.execute(sql.format(product_id, product_name, product_price, product_category, prescription_required, expiry_date, discount))

      mycursor.execute("INSERT INTO sells Values({}, {}, {})".format(seller_id, product_id, quantity))
      
    elif (o==2):
      p_id = int(input("Enter Product ID of product whose stock is to be updated: "))

      q = int(input("Enter updated quantity of the product: "))

      mycursor.execute("UPDATE sells SET quantity = {} WHERE product_id = {} AND seller_id = {}".format(q, p_id, seller_id))

    elif (o==3): 
      break

def admin_page(admin_id):

  while(True): 
    o = int(input("\n1. View a log of all Orders \n2. Cancel an order \n3. Verify/Disallow Prescription \n4. Set Discount on a Product \n5. Change price of a Product \n6. Change status of an Order\n7. Sign out\n\nChoose option: "))
    
    print()
    print()
    if (o==1):
      print()
      mycursor.execute("SELECT * FROM _order")
      rows = mycursor.fetchall()

      for row in rows:
        print(row)

    elif (o==2):
      o_id = int(input("Enter order ID of order to be cancelled: "))
      mycursor.execute("UPDATE my_orders SET status = 'CANCELLED' WHERE order_id = {} ".format(o_id))

      print("\nOrder (#{}) cancelled! \n".format(o_id))

      mycursor.execute("Select quantity, product_id from _contains where order_id = {}".format(o_id))
      rows = mycursor.fetchall()
      i=0
      for row in rows:
        if (i==0):
          i+=1
          continue
        
        mycursor.execute("UPDATE sells SET quantity = quantity + {} WHERE product_id = {}".format(int(row[0]), rows[1]))

    elif (o==3):
      mycursor.execute("Select * from prescription where admin_id IS NULL")
      print("\n\n")
      
      rows = mycursor.fetchall()

      for row in rows:
        print(row)

      p_id = int(input("\n\nEnter prescription ID to be verified: "))
      status = int(input("Enter 1 to Invalidate prescription, Enter 2 to Validate Prescription: "))

      if (status == 1):
        mycursor.execute("UPDATE prescription SET admin_id = {} Where prescription_id = {}".format(admin_id, p_id))

        mycursor.execute("Select order_id from my_prescription WHERE prescription_id = {}".format(p_id))
        rows = mycursor.fetchall()
        i=0
        for row in rows:
          if (i==0):
            i+=1
            continue

          mycursor.execute("UPDATE my_orders SET status = 'Prescription Denied' WHERE order_id = {}".format(row[0]))

          o_id = row[0]
          mycursor.execute("Select quantity, product_id from _contains where order_id = {}".format(o_id))
          rows_ = mycursor.fetchall()
          i=0
          for row in rows_:
            if (i==0):
              i+=1
              continue

            mycursor.execute("UPDATE sells SET quantity = quantity + {} WHERE product_id = {}".format(int(row[0]), rows[1]))
      elif (status == 2):
        mycursor.execute("UPDATE prescription SET admin_id = {}, usage_count = usage_count + 1 WHERE prescription_id = {}".format(admin_id, p_id))

        mycursor.execute("Select order_id from my_prescription WHERE prescription_id = {}".format(p_id))
        rows = mycursor.fetchall()
        for i in len(rows):
          if (i==0):
            continue

          mycursor.execute("Update my_orders SET status = 'Out For Delivery' where order_id = {}".format(rows[i][0]))

    elif (o==4):
      p_id = int(input("Enter product ID of product to be discounted: "))
      d = int(input("Enter % of discount to be applied: "))

      mycursor.execute("Update product set discount = {} where product_id = {}".format(d, p_id))

      print("Discount of {} percent set on Product(#{})".format(d, p_id))

    elif (o==5):
      p_id = int(input("Enter product ID of product whose price is to be updated: "))
      d = int(input("Enter new price of the product: "))

      mycursor.execute("Update product set Product_Price = {} where product_id = {}".format(d, p_id))

      print("Price updated of Product(#{})".format(p_id))

    elif(o==6):
      o_id = int(input("Enter order ID of the ordder whose status is to be updated: "))
      d = int(input("Enter new status of the order: "))
      
      mycursor.execute("Update my_orders set status = '{}' where order_id = {}".format(d, o_id))

      print("Updated status of the Order(#{}) is {}".format(o_id, d))

    elif(o==7):
      break

def landing_page():
  
  while (True):
    print("\n\n\t\t\t\t WELCOME TO PHARMA MART")

    for i in range(1):
      print()
    option  = int(input("\n\n1. Register New Account \n2. Login \n3. Exit \n\nChoose option: "))  

    if(option==1):
      option2 = int(input("\n1. Register as Customer\n2. Register as Seller \n3. Register as Admin \n4. Go back\n\nChoose option: "))
      if (option2==4):
        continue
      register(option2)
    
    elif(option==2):
      option2 = int(input("\n1. Login as Customer \n2. Login as Seller \n3. Login as Admin\n\nChoose option: "))
      out = login(option2)
      if (out!=0):
        if (out[0]==1):
          Home(out[1])

        elif (out[0]==2):
          seller_page(out[1])
        
        elif (out[0]==3):
          admin_page(out[1])
        
        elif (option==4):
          continue

    elif(option==3):
      exit()

    
    else:
      print("Select a valid option!\n")


#Chaudhary

def categories(cust_ID):
  SQL="SELECT DISTINCT PRODUCT_CATEGORY FROM PRODUCT"
  mycursor.execute(SQL)
  Rows= mycursor.fetchall()
  for i in range(len(Rows)):
    print(f"{i + 1}) {Rows[i][0]}")
  while True:
    choice = input("\n\nPlease select a category number from the above mentioned options or write cart to show cart: ")
    if (choice == "cart"):
      cart(cust_ID)
    elif (choice.isnumeric() == True):
      break

  mycursor.execute("Select account_id from pharmamart_account where customer_id = {}".format(cust_ID))
  row = mycursor.fetchone()
  products(int(choice)-1, cust_ID, int(row[0]))

def products(choice_n, cust_ID, account_id):
    cat = ""
    _SQL="select * from distinct_categories"
    mycursor.execute(_SQL)  
    _Rows= mycursor.fetchall()
    cat = _Rows[choice_n][0]
    print("categor select : ", cat)
    SQL = "SELECT PRODUCT_ID, PRODUCT_NAME FROM PRODUCT WHERE PRODUCT_CATEGORY = '{}'".format(cat)
    mycursor.execute(SQL)
    Rows = mycursor.fetchall()
    for i in Rows:
      print(i)
    # choice = input("\n\nPlease select a Product_ID from the above mentioned options or write cart to show cart or home to go to Home Page: ")
    while True:
      choice = input("\n\nPlease select a Product_ID from the above mentioned options or write cart to show cart or home to go to Home Page: ")
      if (choice == "cart"):
        mydb.commit()
        cart(cust_ID)
        break
      elif (choice == "home"):
        Home(cust_ID)
        break
      elif (choice.isnumeric() == True):
        break
    SQL = "SELECT PRODUCT_ID, PRODUCT_NAME, PRODUCT_PRICE, PRESCRIPTION_REQUIRED, EXPIRY_DATE FROM PRODUCT WHERE PRODUCT_ID = {} AND product_category = {} ".format(choice, choice_n)
    mycursor.execute(SQL)
    Rows = mycursor.fetchall()
    for i in Rows:
      print(i)
    # choice_nos = input("\n\nPlease enter the quantity of the above product to be added to cart or write cart to show cart or home to go to Home Page: ")
    while True:
      choice_nos = input("\n\nPlease enter the quantity of the above product to be added to cart or write cart to show cart or home to go to Home Page: ")
      if (choice_nos.lower() == "cart"):
        cart(cust_ID)
      elif (choice_nos.lower() == "home"):
        Home(cust_ID)
      elif (choice_nos.isnumeric() == True):
        break
    SQL = "SELECT seller_id, Quantity FROM SELLS WHERE PRODUCT_ID = " + choice
    mycursor.execute(SQL)
    Rows = mycursor.fetchall()
    valueis = 0
    for i in Rows:
      valueis += i[1]
    # valueis = sum(Rows)
    while (int(choice_nos) > valueis):
        print("Sorry! The quantity entered exceeds the quantity available for this product. The max quantity that can be ordered is " + str(valueis))
        while True:
          choice_nos = input("\n\nPlease enter the quantity of the above product to be added to cart or write cart to show cart or home to go to Home Page: ")
          if (choice_nos.lower() == "cart"):
            cart(cust_ID)
          elif (choice_nos.lower() == "home"):
            Home(cust_ID)
          elif (choice_nos.isnumeric() == True):
            break
    i = 0
    choice_nos = int(choice_nos)
    while choice_nos > 0:
      if choice_nos < Rows[i][1]:
        SQL = f"INSERT INTO CART VALUES({cust_ID}, {account_id}, {choice}, {Rows[i][0]}, {choice_nos})"
        mycursor.execute(SQL)
        mydb.commit()
        break
      SQL = f"INSERT INTO CART VALUES({cust_ID}, {account_id}, {choice}, {Rows[i][0]}, {Rows[i][1]})"
      mycursor.execute(SQL)
      choice_nos -= Rows[i][1]
      i += 1  
    print_cart(cust_ID, choice)

    mydb.commit()

def print_cart(cust_ID, Product_ID):
  SQL = "SELECT PRODUCT_NAME, Product_price, Quantity, Discount FROM (Cart natural join Product) WHERE customer_id = " + str(cust_ID)  + " and Product_ID = " + str(Product_ID)
  mycursor.execute(SQL)
  Rows = mycursor.fetchall()
  Cart_total = 0
  for i in Rows:
    Cart_total = (i[1]*i[2] * (100 - i[3]) / 100)
  print(f"{Rows[0][2]} quantities of {Rows[0][0]} amounting ruppees {Cart_total} have been added to cart.")
  categories(cust_ID)

def cart(cust_ID):
  #Discount product attribute, total = i[2]
  # mycursor.execute("Select account_id from pharmamart_account where customer_id = {}".format(cust_ID))
  # acc_id = (mycursor.fetchone())[0]
  SQL = "SELECT PRODUCT_ID, PRODUCT_NAME, Product_price, Quantity, Discount FROM (Cart natural join Product) WHERE customer_id = " + str(cust_ID)
  mycursor.execute(SQL)
  Rows = mycursor.fetchall()
  Cart_total = 0

  L = list()
  print("PRODUCT_ID, PRODUCT_NAME, PRODUCT_PRICE, QUANTITY, DISCOUNT")
  for i in Rows:
    print(f"({i[0]}, {i[1]}, {i[2]}, {i[3]}, {i[4]}%)")
    Cart_total = (i[2]*i[3] * (100 - i[4]) / 100) + Cart_total
    L.append([i[0], i[3]])
  print("\nTotal Cart Value:", Cart_total)
  check_out = input("1. Checkout cart\n2. Empty Cart\n3. Go Back to Home Page\n\nChoose option: ")
  print()
  if (check_out.lower() == "1"):
    mydb.commit()
    checkout(L, Cart_total, cust_ID)
  elif (check_out.lower() == "2"):
    sql = "DELETE FROM cart WHERE customer_id = {}".format(cust_ID)
    mycursor.execute(sql)
    print("\nCart Emptied\n")
    mydb.commit()
    Home(cust_ID)
  else:
    mydb.commit()
    Home(cust_ID)

  mydb.commit()
  
def my_orders(cust_ID):
  SQL = "SELECT Order_ID, Date_of_order, total_price, shipping_agent, tracking_link FROM _Order Natural JOIN MY_ORDERS WHERE CUSTOMER_ID = " + str(cust_ID)
  mycursor.execute(SQL)
  Rows = mycursor.fetchall()
  for i in Rows:
    print(i)
  choice = input("\n\nPlease select a ORDER_ID from the above mentioned options or write cart to show cart or home to go to Home Page: ")
  SQL = "SELECT order_id, PRODUCT_ID, PRODUCT_NAME, PRODUCT_PRICE, Quantity FROM _ORDER NATuRAL JOIN _contains NATURAL JOIN Product WHERE Order_ID = " + str(choice)
  mycursor.execute(SQL)
  Rows = mycursor.fetchall()
  for i in Rows:
    print(i)

  Home(cust_ID)

def Customer_profile(cust_ID):
  print()
  SQL = "SELECT FirstName, MiddleName, Lastname, address_houseno, dob, phone_number, Email, wallet_balance FROM (Customer natural Join pharmamart_account) WHERE CUSTOMER_ID = " + str(cust_ID)
  mycursor.execute(SQL)
  Rows = mycursor.fetchall()
  for i in Rows:
    print(i)

  o=int(input("\n1. View your orders\n2. View Wallet Balance \n3. Add Money to Wallet \n4. Change Password\n5. Go back\nChoose option: "))
  if (o==3):
    while True:
      try:
        money_added = float(input("\nEnter money to be added: "))
        break
      except:
        continue
    OTP = int(input("Enter OTP: ")) #0000
    if (OTP == 0):
      money_added = money_added + Rows[0][7]
      SQL = "Update pharmamart_account set wallet_balance = " + str(money_added) + " WHERE CUSTOMER_ID = " + str(cust_ID)
      mycursor.execute(SQL)
      # mydb.commit()
      # TEMPORARILY COMMENTED
  elif (o==1):
    my_orders(cust_ID)
  
  elif (o==2):
    quer = "Select wallet_balance from pharmamart_account where customer_id = " + str(cust_ID)
    mycursor.execute(quer)
    
    balance = mycursor.fetchone()[0]

    print("\nYour Wallet Balance is: Rs.", balance, "\n", sep = " ")

  elif (o==4):
    print()
    s = "select username from customer where customer_id = {}".format(cust_ID)
    mycursor.execute(s)
    username = mycursor.fetchone()[0]

    while (True):
      password = input("\nEnter old password: ")
      q = "Select * from credentials C join customer WHERE C.username = '" +username+ "' AND C.passwd = '" + password + "'"

      mycursor.execute(q)
      rows_cred = mycursor.fetchall()
      if (len(rows_cred) == 0):
        o = int(input("Password Incorrect!\n\nPress 1 to try again or 2 to go Back: "))
        if (o==1):
          continue
        else:
          mydb.commit()
          Home(cust_ID)

      else:
        pas = input("Enter new Password: ")
        q2 = "UPDATE credentials SET password = {} where username = {}".format(pas, username)
        mycursor.execute(q2)
        print("\nPassword Changed successfully!\n")
        mydb.commit()
        break

    Home(cust_ID)
        

  else:
    mydb.commit()
    Home(cust_ID)

def Home(customer_id):
  
  while(True):
    o = int(input("\n1. Show Categories \n2. Profile Page \n3. View Cart\n4. Log Out\n\nChoose option: "))

    if (o==1):
      categories(customer_id)
    elif(o==2):
      Customer_profile(customer_id)

    elif(o==3):
      cart(customer_id)

    elif(o==4):
      landing_page()

landing_page()

mycursor.close()
mydb.commit()
mydb.close()