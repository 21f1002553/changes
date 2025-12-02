# How to Run This Vue.js Application Locally

This guide provides step-by-step instructions to get the expense management application running on your local computer.

## 1. Prerequisites

Before you begin, ensure you have **Node.js** installed on your system. This project was developed using **Node.js version 20.x** or later.

> You can download the latest version of Node.js from [https://nodejs.org/](https://nodejs.org/).

## 2. Installation

Once you have downloaded the project files, navigate to the root directory of the project in your terminal and run the following command to install all the required dependencies listed in the `package.json` file.

```bash
npm install
```

This command will download and install all necessary libraries, including Vue, Vite, Chart.js, and others.

## 3. Running the Development Server

After the installation is complete, you can start the local development server by running the following command:

```bash
npm run dev
```

This command starts the Vite development server. You will see output in your terminal indicating that the server is running, similar to this:

```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

## 4. Viewing the Application

Open your web browser and navigate to the local URL provided in the terminal (by default, it is **http://localhost:5173**).

You should now see the running application. The development server provides Hot Module Replacement (HMR), which means that any changes you save in the source code will be reflected in the browser almost instantly without needing a full page reload.
