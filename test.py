import datetime

def validate_format(inp):
    try:
       return datetime.datetime.strptime(inp,"%Y-%m-%d")
    except:
       print("podaj dobry format!")
       inp = input()

       validate_format(inp)

inp = input()
validate_format(inp)
print(inp)
