# Jenkins Manual Testing Demo

## 📌 Overview
The **Jenkins Manual Testing Demo** is a project designed to showcase how **manual testing** can be seamlessly integrated into a **Jenkins CI/CD pipeline**. While Jenkins is widely used for automation, certain **exploratory, usability, and regression testing** tasks still require manual intervention. This project demonstrates an effective **hybrid testing** approach where **testers can be involved in the CI/CD process** while ensuring high software quality before deployment.

---

## 🎯 Objectives
- ✅ **Integrate Manual Testing into a Jenkins Pipeline.**
- ✅ **Enable Test Case Execution Tracking within Jenkins.**
- ✅ **Ensure a Hybrid Approach** combining automation and manual testing.
- ✅ **Facilitate Test Execution Reporting & Logging in Jenkins.**
- ✅ **Notify Testers & Stakeholders** via email or messaging platforms.

---

## 🏗️ Workflow
1. **Code Commit & Pipeline Trigger** – Developers commit code to the repository, triggering the Jenkins pipeline.
2. **Build & Automated Tests** – Unit tests and automated tests run first.
3. **Manual Testing Stage** – The pipeline pauses, waiting for manual tester input.
4. **Tester Execution** – Testers manually execute test cases and approve/reject the build.
5. **Deployment Decision** – If tests pass, the pipeline continues; otherwise, it halts for fixes.
6. **Reporting & Notifications** – Jenkins logs the test results and notifies the team.

---

## 🛠️ Tech Stack
- **Jenkins** (CI/CD Automation)
- **Test Management Tools** (Jira, TestRail, Excel)
- **Scripting** (Shell, Python, Groovy)
- **Notification Systems** (Slack, Email, Teams)
- **Version Control** (GitHub, Git, Bitbucket)

---

## 🚀 Setup Instructions
### 📌 Prerequisites
- **Jenkins installed** (latest version recommended)
- **Git Repository** for the project
- **Test Cases Documented** (Excel, Jira, or TestRail)
- **Jenkins Plugins**:
  - Pipeline Plugin
  - Email Extension Plugin (optional for notifications)
  - Input Step Plugin (for manual test stage)

### 📌 Installation Steps
1. **Clone the repository**:
   ```sh
   git clone https://github.com/your-repo/Jenkins-Manual-Testing-Demo.git
   cd Jenkins-Manual-Testing-Demo
