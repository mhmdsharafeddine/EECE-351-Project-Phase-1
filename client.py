from socket import *
import json
import threading
import os
from PIL import Image
from colorama import init, Fore, Style, Back
from datetime import datetime
import io
def commands():
        port=int(input("Please enter a Port Number: "))
        try:
            client = socket(AF_INET, SOCK_STREAM)
            client.connect(("127.0.0.1", port))
            chatsocket = socket(AF_INET,SOCK_STREAM)
            chatsocket.connect(("127.0.0.1",port))
            Options1=["Register","Login"]
            print(Options1)
            choice=input("Please choose one of the following options: ")
            
            while (choice not in Options1):
                print("No such task.")
                print(Options1)
                choice=input("Please choose one of the above options: ")
            
            
            if(Options1[0]==choice):
                register_client(client)
                threading.Thread(target=receive_messages, args=(chatsocket,), daemon=True).start()
                commands2(client,chatsocket)
            else:
                login_client(client)
                threading.Thread(target=receive_messages, args=(chatsocket,), daemon=True).start()
                commands2(client,chatsocket)
            client.close()
        except Exception as e:
            print(f"Erorr: {e}")
            client.close()

def commands2(client,chatsocket):
            Options2=["Add product","View products of","View Picture of certain product of owner", "View my customers","Buy product","Chat", "Logout"]
            x=False
            while True:
                if (x==False):
                    view_products_client(client)
                    print()
                    print(Options2)
                    choice2=input("Please choose one of the following options: ")
                x=False
                if (choice2==Options2[0]):
                    add_product_client(client)
                #elif (choice2==Options2[1]):
                    #remove_product_client(client, "")
                elif(choice2==Options2[1]):
                    products_of_client(client)
                elif(choice2==Options2[2]):
                    image_of_product(client)
                elif(choice2==Options2[3]):
                    my_Customers_client(client)
                elif(choice2==Options2[4]):
                    buy_product_client(client)
                elif(choice2 ==Options2[5]):
                    chat_with_user(chatsocket,client)
                elif(choice2==Options2[6]):
                    client.send("Logout".encode())
                    print("Good bye")
                    break
                else:
                    while (choice2 not in Options2):
                        print("No such task.")
                        print(Options2)
                        choice2=input("Please choose one of the above options: ")
                        x=True

def image_of_product(client):
    client.send("View picture of a specific product of a buyer".encode())
    try:
        username=input("Enter the username of the owner: ")
        client.send(username.encode()) 
        x=client.recv(1024).decode()
        while(x=="Invalid username"):
           username=input("Enter the correct username of the owner: ")
           client.send(username.encode())
           x=client.recv(1024).decode()
        
        name=input("Enter the name of the product: ")   
        client.send(name.encode())
        x=client.recv(1024).decode()
        while(x=="Invalid product"):
           name=input("Enter the correct name of the product: ")
           client.send(name.encode())
           x=client.recv(1024).decode()
        size=int(client.recv(1024).decode())
        data=client.recv(size)
        image = Image.open(io.BytesIO(data))
        image.show()
    except Exception as e:
       print(f"Error: {e}")
    
def buy_product_client(client):
    try:
        client.send("Buy product".encode())
        x="1"
        while x=="1":
            response=client.recv(1024).decode()
            print(response)
            u=input("")
            client.send(u.encode())
            d=client.recv(1024).decode()
            if (d=="No such product"):
                print(d)
                print(client.recv(1024).decode())
                l=input("")
                client.send(l.encode())
                if (l!="1"):
                    break
            else:
                d1=json.loads(d)
                print()
                for key in d1:
                    for x in d1[key]:
                        print(key+ ":" +str(x))
                choice=input("Enter the choice you need to purchase.")
                client.send(choice.encode())
                print(client.recv(1024).decode())
                print(client.recv(1024).decode())
                x=input("")
                client.send(x.encode())
                

    except Exception as e:
        print(f"Error: {e}")

def view_products_client(client):
    print()
    print("Main Page: ")
    try:
        d=client.recv(1024).decode()
        if (d=="No products on the server."):
            print(d)
        else:
            print("Products are:")
            
           
            d1=json.loads(d)
            for key in d1:
                for x in d1[key]:
                    print(key+" : "+str(x))
    
    except Exception as e:
        print(f"Error: {e}") 

def my_Customers_client(client):
    try:
        client.send("View my customers".encode())
        d=client.recv(1024).decode()
        if (d=="You have no products."):
            print(d)
        else:
            d1=json.loads(d)
            response=client.recv(1024).decode()
            print(response)
            for key in d1:
                print(key+" : "+d1[key])
    
    except Exception as e:
        print(f"Error: {e}")

def add_product_client(client):    
    try:
        client.send("Add product".encode())
        response=client.recv(1024).decode()
        print(response)
        if response=="Ready to add":
            product_name=input("Enter product name: ")
            client.send(product_name.encode())
            u=client.recv(1024).decode()
            if u=="Insert the price: ":
                print(u)
                price=input("")
                try:
                    price=float(price)
                except:
                    while True:
                        print("Wrong input.")
                        price=input("Enter a real number: ")
                        try:
                            price=float(price)
                            break
                        except:
                            z=1 
                client.send(str(price).encode())
                print(client.recv(1024).decode())
                description=input("")
                client.send(description.encode())
                print(client.recv(1024).decode())
                image=input("")
                while True:
                    try:
                        if (image[-5:]== ".jpeg" or image[-4:]==".png" or image[-4:]==".jpg"):
                            with open(image, 'rb') as file:
                                image_data=file.read()
                            file.close()
                            break
                        else:
                            print("Wrong input")
                            image=input("Please enter the correct image :")
                    except:
                        print("No such image")
                        image=input("Please enter the correct image :")
                client.send(image.encode())
                image_client(client,image)
                print(client.recv(1024).decode())
            else:
                print(u)

            
            
    except Exception as e:
        print(f"An error occured: {e}")

def image_client(client,image):
    with open(image, 'rb') as file:
        image_data=file.read()
        client.send(image_data)
    file.close()

def remove_product_client(client,p):
    try:
        client.send("Remove product".encode())
        response=client.recv(1024).decode()
        print(response)
        if response=="Ready to remove":
            p=input("Enter the name of the product you want to remove: ")
            client.send(p.encode())
            response=client.recv(1024).decode()
            print(response)
    except Exception as e:
            print(f"An error occurred: {e}")
        
def products_of_client(client):
    try:
        client.send("View products of".encode())
        response=client.recv(1024).decode()
        print(response)
        u=input("")
        client.send(u.encode())
        
        d=client.recv(1024).decode()
        if (d=="This user has no products for sale."):
            print(d)
        elif(d=="There is no such user"):
            print(d)
        else:
            d1=json.loads(d)
            for key in d1:
                    print(key+ str(d1[key]))
    
    except Exception as e:
        print(f"Error: {e}")  
        
def register_client(client):
    # Connect to the server
    try:
        # Start the registration process
        client.send("Register".encode())
        response = client.recv(1024).decode()
        print(response)
        # Input user details
        if response == "Ready to register":
            name=input("Enter full name: ")
            client.send(name.encode())
            username = input("Enter username: ")
            client.send(username.encode())
            while(client.recv(1024).decode()=="Change username"):
                username= input("Enter another username: ")
                client.send(username.encode())
            email = input("Enter email: ")
            client.send(email.encode())
            while (client.recv(1024).decode()=="Another mail"):
                email= input("Enter a new Email: ")
                client.send(email.encode())
            password = input("Enter password: ")
            client.send(password.encode())
            print(client.recv(1024).decode())
            print("We are done") 
    except Exception as e:
        print(f"An error occurred: {e}")

def login_client(client):
        try:
            client.send("Login".encode())
            response=client.recv(1024).decode()
            print(response)
            if(response=="Ready to login"):
                username=input("Enter username: ")
                client.send(username.encode())
                if(client.recv(1024).decode()=="Username isnt found"):
                    print("Username isnt correct")
                    username=input("Enter username: ")
                    client.send(username.encode())
                    while(client.recv(1024).decode()=="Username isnt found"):
                        print("Username isnt correct")
                        username=input("Enter username: ")
                        client.send(username.encode())
                password=input("Enter password: ")
                client.send(password.encode())
                if(client.recv(1024).decode()=="Incorrect Password"):
                    print("Password isnt correct")
                    password=input("Enter password: ")
                    client.send(password.encode())
                    while(client.recv(1024).decode()=="Incorrect Password"):
                        print("Password isnt correct")
                        password=input("Enter password: ")
                        client.send(password.encode())
            print(client.recv(1024).decode())
        except Exception as e:
            print(f"Error: {e}")
  







def send_message(client, message):
    try:
        client.send(message.encode("utf-8"))
    except Exception as e:
        print(f"Failed to send message: {e}")



def start_chat(client):
    threading.Thread(target=receive_messages, args=(client,), daemon=True).start()
    print("To chat with a user, prefix their name with '@' and suffix with '/'")

    while True:
        message = input("You: ")
        if message.lower() == "exit":
            break
        else:
            send_message(client, message)

def chat_with_user(chatsocket, client_socket):
    client_socket.send("Chat".encode())
    print("\n=== Starting Chat Session ===\n")
    
    response = client_socket.recv(1024).decode()
    if "Enter the username" in response:
        target_user = input("Username to chat with: ")
        client_socket.send(target_user.encode())
        online_status = client_socket.recv(1024).decode()
        print(online_status)
        
        if "Start chatting" in online_status:
    
            print("\nType your messages below. Type 'exit chat' to end the conversation.")
            print("=" * 50 + "\n")
            
            while True:
                timestamp = datetime.now().strftime("%H:%M")
                message = input(f"\033[94m[{timestamp}] You:")
                if message.lower() == "exit chat":          
                    print("\n=== Chat Session Ended ===\n")
                    break
                chatsocket.send(message.encode())


def receive_messages(chatsocket):
    while True:
        try:
            message = chatsocket.recv(1024).decode('utf-8')
            if message:
                message = message.strip()
                timestamp = datetime.now().strftime("%H:%M")
                print(f"\033[92m[{timestamp}] Them: {message}\033[0m")
                
        except Exception as e:
            print(f"\n\033[91mConnection error: {str(e)}\033[0m")
            break









            
commands()
