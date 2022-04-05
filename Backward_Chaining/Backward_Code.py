from PyInquirer import prompt
import mysql.connector
from examples import custom_style_3

final_c=list()
final_c_id=0
choice=[]
answers=[]
cf=[]
cf_tmp=[]
final_variable='recommend_monitor'

mydb= mysql.connector.connect(
    host="localhost",
    username="root",
    password="",
    database="asp"
)

def diplay_questions_and_choice(name,question,choice): #menggunakan PyInquirer
    questions = [
        {
            'type': 'list',
            'name': name,
            'message': question + " : ",
            'choices': choice
        }
    ]
    return questions

def update_sign():
    # Update table menjadi 'True' yang memenuhi syarat 
    mycursor.execute("SELECT premise_id FROM premise WHERE variable ='"+answers[0][0]+"' AND value='" + answers[0][1] + "'" )
    myresult=mycursor.fetchall()
    mycursor.execute("UPDATE rule_premise2 SET premise_sign = 'TU' WHERE premise_id='"+ str(myresult[0][0]) +"'")
    mydb.commit()

    # Update table menjadi 'False' yang tidak memenuhi syarat 
    mycursor.execute("SELECT premise_id FROM premise WHERE variable ='"+answers[0][0]+"' AND value!='" + answers[0][1] + "'" )
    myresult=mycursor.fetchall()
    for i in range(len(myresult)):
        mycursor.execute("UPDATE rule_premise2 SET premise_sign = 'FA' WHERE premise_id='"+ str(myresult[i][0])+"'")
        mydb.commit()

    # Update Rules menjadi 'Deleted' yang tidak memenuhi syarat (Akan di update trs padahal sdh 'D')
    mycursor.execute("SELECT DISTINCT rule_id FROM rule_premise2 WHERE premise_sign='FA'" )
    myresult=mycursor.fetchall()
    for i in myresult:
        mycursor.execute("UPDATE rule2 SET rule_sign = 'D' WHERE rule_id='"+str(i[0])+"'")
        mydb.commit()

    #Mengecek rule mana yang sudah memenuhi dan update menjadi "Terminated"
    mycursor.execute("SELECT rule_id FROM rule_premise2 GROUP BY rule_id HAVING COUNT(IF(premise_sign='TU',1,NULL)) = COUNT(premise_id)" )
    myresult=mycursor.fetchall()
    for i in myresult:
        mycursor.execute("UPDATE rule2 SET rule_sign = 'TD' WHERE rule_id='"+str(i[0])+"'")
        mydb.commit()
  

#Pilih Rule set dengan final variable
mycursor=mydb.cursor(buffered=True)
mycursor.execute("SELECT rule_id, final_conclusion FROM rule2 WHERE rule_id = 9")
myresult=mycursor.fetchone()

#Mengambil Premise-premise nya
mycursor.execute("SELECT p.variable FROM premise p JOIN rule_premise2 rpt ON p.premise_id=rpt.premise_id WHERE rpt.rule_id="+str(myresult[0])+"")
myresult=mycursor.fetchall()
premise=[]
lvl_2=[]
for i in myresult:
    premise.append(i[0])
s=int(0)

#Memunculkan pertanyaan sesuai premise-premise yg disimpan
while s !=len(premise)+1:
    if len(answers) == 0:
        mycursor.execute("SELECT rule_id FROM rule2 WHERE rule_variable='"+premise[s]+"'")
        myresult=mycursor.fetchall()
        if len(myresult) ==0:
            mycursor.execute("SELECT question_id,question FROM question WHERE variabel='"+premise[s]+"'")
            myresult=mycursor.fetchall()
            mycursor.execute("SELECT choice FROM choice WHERE question_id=" + str(myresult[0][0]))
            myresult2=mycursor.fetchall()
            for i in myresult2:
                choice.append(i[0])  
            pick = prompt(diplay_questions_and_choice(premise[s],myresult[0][1],choice), style=custom_style_3)
            
            input_cf=input("Nilai CF (0-1): ")
            if input_cf >'1.0' or input_cf=='': input_cf='1.0'
            elif input_cf <'0.0': input_cf='0.0'
            answers.extend(pick.items())
            choice.clear()
            s+=1
            print()
        else:
            mycursor.execute("SELECT p.variable FROM premise p JOIN rule_premise2 rpt ON p.premise_id=rpt.premise_id WHERE rpt.rule_id="+str(myresult[0][0])+"")
            myresult=mycursor.fetchall()
            idx=premise.index(premise[s])
            premise.remove(premise[s])
            for i in myresult:
                premise.insert(idx,i[0])
            cf_tmp.extend(cf)
            cf.clear()
    else:
        update_sign()
        cf.append(float(input_cf))
        #Mengecek rule yang "Terminated" dan mengecek variable nya
        mycursor.execute("SELECT rule_variable,final_conclusion,cf FROM rule2 WHERE rule_sign='TD'" )
        myresult=mycursor.fetchall()
        if len(myresult) !=0:       
            for i in myresult:
                if i[0]==final_variable:
                    cf_tmp.extend(cf)
                    print("Monitor yang di rekomendasi : ", i[1])
                    print("Final CF = ", min(cf_tmp)*i[2])
                    s=len(premise)+1
                    break
                elif (i[0],i[1]) not in lvl_2:
                    lvl_2.append((i[0],i[1]))
                    answers.append((i[0],i[1]))
                    ttl_cf=min(cf)*i[2]
                    print("CF sementara : ", ttl_cf)
                    cf_tmp.append(ttl_cf)
                    cf.clear()               
        answers.pop(0)
        

input("Press Any Key...")
mycursor.execute("UPDATE rule2 SET rule_sign = 'A,U'")
mydb.commit()
mycursor.execute("UPDATE rule_premise2 SET premise_sign = 'FR'")
mydb.commit()








    

