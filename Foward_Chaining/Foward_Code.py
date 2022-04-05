import mysql.connector
from PyInquirer import prompt
from examples import custom_style_3


questions=list()
questions_id=0
choice=[]
final_variable='recommend_monitor'
counter = 0

mydb= mysql.connector.connect(
    host="localhost",
    username="root",
    password="",
    database="asp"
)

def diplay(monitor,choice,question):
    questions = [
        {
            'type': 'list',
            'name': monitor,
            'message': question + " : ",
            'choices': choice
        }
    ]
    return questions

mycursor=mydb.cursor()
mycursor.execute("SELECT q.question, q.variabel FROM question q")
myresult=mycursor.fetchall()


for i in myresult:
    questions.append(i)
    questions_id+=1  
    
print("\n-> Silahkan memilih spesifikasi monitor <-")
s=int(0)
answers=[]
lvl_2=[]
while s!=questions_id+1: 
    if len(answers) == 0:  
        mycursor.execute("SELECT c.choice FROM choice c WHERE c.question_id =" + str((s+1)))
        myresult=mycursor.fetchall() 
        for i in myresult:
            choice.append(i[0])  
        pick = prompt(diplay(questions[s][1],choice,questions[s][0]), style=custom_style_3)
        answers.extend(pick.items())
        choice.clear()
        s+=1
    mycursor.execute("SELECT premise_id FROM premise WHERE variable ='"+answers[0][0]+"' AND value='" + answers[0][1] + "'" )
    myresult=mycursor.fetchall()
    mycursor.execute("UPDATE rule_premise SET premise_sign = 'TU' WHERE premise_id='"+ str(myresult[0][0]) +"'")
    mydb.commit()

    mycursor.execute("SELECT premise_id FROM premise WHERE variable ='"+answers[0][0]+"' AND value!='" + answers[0][1] + "'" )
    myresult=mycursor.fetchall()
    for i in range(len(myresult)):
        mycursor.execute("UPDATE rule_premise SET premise_sign = 'FA' WHERE premise_id='"+ str(myresult[i][0])+"'")
        mydb.commit()

    mycursor.execute("SELECT DISTINCT rule_id FROM rule_premise WHERE premise_sign='FA'" )
    myresult=mycursor.fetchall()
    for i in myresult:
        mycursor.execute("UPDATE rule SET rule_sign = 'D' WHERE rule_id='"+str(i[0])+"'")
        mydb.commit()

    mycursor.execute("SELECT rule_id FROM rule_premise GROUP BY rule_id HAVING COUNT(IF(premise_sign='TU',1,NULL)) = COUNT(premise_id)" )
    myresult=mycursor.fetchall()
    for i in myresult:
        mycursor.execute("UPDATE rule SET rule_sign = 'TD' WHERE rule_id='"+str(i[0])+"'")
        mydb.commit()
        
    mycursor.execute("SELECT rule_variable,final_conclusion FROM rule WHERE rule_sign='TD'" )
    myresult=mycursor.fetchall()

    if len(myresult) !=0:
        for i in myresult:
            if i[0]==final_variable:
                print("\n-> Merk monitor yang di rekomendasikan : Monitor ", i[1])
                s=questions_id+1
                break
            elif (i[0],i[1]) not in lvl_2:
                lvl_2.append((i[0],i[1]))
                answers.append((i[0],i[1]))
            print(answers)
                
    answers.pop(0)
    
    
mycursor.execute("UPDATE rule SET rule_sign = 'A,U'")
mydb.commit()
mycursor.execute("UPDATE rule_premise SET premise_sign = 'FR'")
mydb.commit()
