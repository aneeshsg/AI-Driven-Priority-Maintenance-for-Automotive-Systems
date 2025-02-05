import streamlit as st
import streamlit.components.v1 as components

html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Automotive Failure Predictive Analysis</title>
  <style>
    :root {
      --primary-color: #4CAF50;
      --text-color: #333;
      --background-color: #f4f4f4;
      --card-background: #fff;
    }
    @media (prefers-color-scheme: dark) {
      :root {
        --primary-color: #4CAF50;
        --text-color: #eee;
        --background-color: #333;
        --card-background: #444;
      }
    }
    body {
      margin: 0;
      font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
      background-color: var(--background-color);
      color: var(--text-color);
    }
    .hero {
      background: var(--primary-color);
      color: #fff;
      padding: 60px 20px;
      text-align: center;
    }
    .hero h1 {
      font-size: 3em;
      margin: 0;
    }
    .hero p {
      font-size: 1.2em;
      margin-top: 10px;
    }
    .cards-container {
      display: flex;
      flex-wrap: wrap;
      justify-content: center;
      margin: 40px 20px;
    }
    .card {
      background-color: var(--card-background);
      box-shadow: 0 2px 5px rgba(0,0,0,0.1);
      border-radius: 8px;
      margin: 10px;
      padding: 20px;
      flex: 1 1 300px;
      max-width: 300px;
      text-align: center;
    }
    .card h2 {
      margin-top: 0;
    }
    .table-section {
      margin: 40px 20px;
    }
    .table-section table {
      width: 100%;
      border-collapse: collapse;
    }
    .table-section th, .table-section td {
      padding: 12px;
      border: 1px solid #ddd;
      text-align: left;
    }
    .table-section th {
      background-color: var(--primary-color);
      color: #fff;
    }
    .footer {
      background: #222;
      color: #fff;
      padding: 20px;
      text-align: center;
    }
  </style>
</head>
<body>
  <!-- Hero Section -->
  <div class="hero">
    <h1>Automotive Failure Predictive Analysis</h1>
    <p>Predict and prevent failures before they occur with our cutting-edge analytics platform.</p>
  </div>
  
  <!-- Cards Section -->
  <div class="cards-container">
    <div class="card">
      <h2>Data Insights</h2>
      <p>Uncover hidden patterns and understand failure trends through comprehensive data analysis.</p>
    </div>
    <div class="card">
      <h2>Real-time Monitoring</h2>
      <p>Stay informed with up-to-the-minute monitoring of automotive performance.</p>
    </div>
    <div class="card">
      <h2>Predictive Analytics</h2>
      <p>Leverage machine learning models to forecast potential failures before they happen.</p>
    </div>
    <div class="card">
      <h2>Actionable Reports</h2>
      <p>Transform data into actionable insights to drive better decision-making.</p>
    </div>
  </div>
  
  <!-- Team Table Section -->
  <div class="table-section">
    <h2 style="text-align: center;">Meet the Team</h2>
    <table>
      <thead>
        <tr>
          <th>Name</th>
          <th>Role</th>
          <th>Contact</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Alice Smith</td>
          <td>Data Scientist</td>
          <td>alice@example.com</td>
        </tr>
        <tr>
          <td>Bob Johnson</td>
          <td>Machine Learning Engineer</td>
          <td>bob@example.com</td>
        </tr>
        <tr>
          <td>Carol Williams</td>
          <td>Software Developer</td>
          <td>carol@example.com</td>
        </tr>
        <tr>
          <td>David Brown</td>
          <td>Project Manager</td>
          <td>david@example.com</td>
        </tr>
      </tbody>
    </table>
  </div>
  
  <!-- Footer -->
  <div class="footer">
    <p>&copy; 2025 Automotive Failure Analysis. All rights reserved.</p>
  </div>
</body>
</html>
"""

st.set_page_config(page_title="Home - Automotive Failure Analysis", layout="wide")
components.html(html_content, height=900)
