# ⚔️ Deployment PoC

## 1. Lab Setup & Scenario
The experimental environment is completely isolated (Sandbox):

| Component | Specifications | Role |
| :--- | :--- | :--- |
| **Attacker (C2 Server)** | Kali Linux (`192.168.x.x`) | Runs Flask Server (Port 1234), manages Agents. |
| **Target (Victim)** | Windows 10/11 (`192.168.x.y`) | Target machine compromised via a malicious executable. |
| **Vector** | Social Engineering / Payload | Victim executes a malicious file (Trojanized Game). |

---

## 2. The Campaign Walkthrough

### 🚩 Step 1: Initial Access & Profiling
The first phase immediately after the payload is executed on the victim's machine.

<div align="center">
  <video src="https://github.com/user-attachments/assets/ad6cda2e-5a37-4d03-8140-0b4da610e2f4" width="900" controls></video>
  <em>Watch the original resolution video here 👉: <a href="https://youtu.be/sdLhr0QD5PE">YouTube Link</a></em>
</div>
<br>

| Aspect | Processing Flow Details |
| :--- | :--- |
| **Progression** | As soon as the file is opened, the Agent secretly collects the system's "fingerprint" (Hostname, OS, CPU, RAM) and sends it to the Server. |
| **Technical Mechanism** | The Agent calls the `check_in()` function, packages data via `psutil` and `platform`, and sends a POST request to the `/api/agent_checkin` API. |
| **Telemetry** | Beaconing starts: The Agent sends CPU/RAM reports every 1 second for the Server to update the Live status. |

---

### 💻 Step 2: Stateful Shell Execution
The administrator controls the target machine via direct command lines.

<div align="center">
  <video src="https://github.com/user-attachments/assets/0040efb3-ddd9-440f-98eb-1cf0ae84dfb0" width="900" controls></video>
  <em>Watch the original resolution video here 👉: <a href="https://youtu.be/LpGVMEryJ0Q">YouTube Link</a></em>
</div>
<br>

| Aspect | Processing Flow Details |
| :--- | :--- |
| **Progression** | `cd`, `dir` operations work smoothly. The system remembers the working directory and doesn't reset after each command. |
| **Technical Mechanism** | The Agent uses the global variable `current_working_dir` combined with `os.chdir()` and `subprocess.run(cwd=...)` to maintain state. |
| **Result** | The Operator has deep access to the victim's file structure, like a real Terminal session. |

---

### 📥 Step 3: Data Infiltration (Additional Payload Deployment)
Pushing other malicious tools from the C2 server to the target machine.

<div align="center">
  <video src="https://github.com/user-attachments/assets/3b6063ca-1d52-43b5-a23e-f62bd482a993" width="900" controls></video>
  <em>Watch the original resolution video here 👉: <a href="https://youtu.be/kmMUwu-p5SA">YouTube Link</a></em>
</div>
<br>

| Aspect | Processing Flow Details |
| :--- | :--- |
| **Progression** | The Operator uses the `upload` command to push a file (e.g., `malware.exe`) from the C2 arsenal to the victim's machine. |
| **Technical Mechanism** | The Server reads the file -> Base64 Encoding -> Sends via JSON. The Agent receives, decodes, and writes it to the target machine's hard drive. |

---

### 📤 Step 4: Exfiltration
Collecting sensitive documents from the victim's machine to the control server.

<div align="center">
  <video src="https://github.com/user-attachments/assets/a3ccb2a9-2696-4fd6-9722-63f90cd65b56" width="900" controls></video>
  <em>Watch the original resolution video here 👉: <a href="https://youtu.be/ym_KG4xskjM">YouTube Link</a></em>
</div>
<br>

| Aspect | Processing Flow Details |
| :--- | :--- |
| **Progression** | Successfully extracted confidential files from the target machine. Data appears immediately in the `c2_downloads` folder. |
| **Technical Mechanism** | The Agent reads the binary file -> Base64 -> POST to `/api/transfer/download`. The Server saves it to the Loot Vault by Agent ID. |

---

### 💨 Step 5: Kill Switch (Retreat & Cover Tracks)
The Agent self-destructs to avoid detection after completing the campaign.

<div align="center">
  <video src="https://github.com/user-attachments/assets/846ca9bb-c35e-4eaf-a31f-bc52e883bb40" width="900" controls></video>
  <em>Watch the original resolution video here 👉: <a href="https://youtu.be/3nUC2m-ALxE">YouTube Link</a></em>
</div>
<br>

| Aspect | Processing Flow Details |
| :--- | :--- |
| **Progression** | Upon receiving the `suicide` command, the Agent immediately removes itself from the Registry startup and terminates the process. |
| **Technical Mechanism** | Calls the `remove_from_startup()` function using `winreg` to delete the Run key. Deletes temporary files and exits with `sys.exit()`. |

---

## 3. Defensive Perspective
From the perspective of a **Blue Team / SOC Analyst**, we can detect labRAT through the following signs:

| Trace Type | Detection Method | Detailed Description |
| :--- | :--- | :--- |
| **Network** | Traffic Analysis | Fixed connection frequency (Beaconing) of 1 second/time to an unknown IP is a clear anomaly. |
| **Host** | Registry Monitoring | The appearance of a strange key `WindowsUpdateService` in `HKCU\...\Run` pointing to an unknown `.exe` file. |
| **Behavior** | Process Tree | The parent process (`agent.exe`) continuously spawns child processes `cmd.exe` executing shell commands. |

> p/s: I tried deploying this system on my friend's machine (Windows 11) with their permission. It can be said that it works as expected (although there are still a few minor bugs). 
---
<p align="center">
  <b>LabRAT Project - Educational Proof of Concept</b>
</p>
