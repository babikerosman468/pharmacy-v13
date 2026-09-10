function webDashboard(){

  const meds = load(DB.MED);
  const sales = load(DB.SALES);

  let revenue = sales.reduce((a,b)=>a+b.total,0);

  const html = `
  <html>
  <head>
    <title>Pharmacy Dashboard</title>
    <style>
      

body {
  font-family: Arial, sans-serif;
  background: #eef7ee;
  color: #2c3e50;
  margin: 20px;
  text-align: center;
}

h1 {
  color: #1b5e20;
}

.card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  margin: 15px;
  display: inline-block;
  min-width: 220px;
  box-shadow: 0 3px 10px rgba(0,0,0,0.12);
}

.medicines {
  border-left: 6px solid #4caf50;
}

.sales {
  border-left: 6px solid #009688;
}

.revenue {
  border-left: 6px solid #0057b8;
}

.alerts {
  border-left: 6px solid #f44336;
}

.value {
  font-size: 26px;
  font-weight: bold;
  color: #0057b8;
}

.footer {
  margin-top: 30px;
  color: #666;
  font-size: 12px;
}

<h1>PHARMACY DASHBOARD V12</h1>

<div class="card medicines">
  <h3>Medicines</h3>
  <div class="value">${meds.length}</div>
</div>

<div class="card sales">
  <h3>Sales</h3>
  <div class="value">${sales.length}</div>
</div>

<div class="card revenue">
  <h3>Revenue</h3>
  <div class="value">${revenue}</div>
</div>

  </body>
  </html>
  `;

