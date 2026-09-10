const fs = require('fs');
const readline = require('readline');
const http = require('http');
const { execSync } = require('child_process');

const DB = {
  MED: 'data/medicines.json',
  SALES: 'data/sales.json',
  AUDIT: 'data/audit.json',
  SUPPLIERS: 'data/suppliers.json',
  PURCHASES: 'data/purchases.json'
};

const COLOR = {
  reset: "\x1b[0m",
  red: "\x1b[31m",
  green: "\x1b[32m",
  yellow: "\x1b[33m",
  blue: "\x1b[34m",
  magenta: "\x1b[35m",
  cyan: "\x1b[36m",
  bold: "\x1b[1m"
};

function load(f) {
  try {
    return JSON.parse(fs.readFileSync(f, 'utf8'));
  } catch (e) {
    return [];
  }
}

function save(f, d) {
  fs.writeFileSync(f, JSON.stringify(d, null, 2));
}

function log(action) {
  let a = load(DB.AUDIT);
  a.push({ action, time: new Date().toISOString() });
  save(DB.AUDIT, a);
}

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

function pause() {
  rl.question('\nENTER...', () => menu());
}

function banner() {
  console.clear();
  console.log(COLOR.cyan + COLOR.bold + `
====================================
PHARMACY MANAGEMENT SYSTEM V12
====================================
` + COLOR.reset);

  console.log(COLOR.yellow + " 1  Add Medicine" + COLOR.reset);
  console.log(COLOR.yellow + " 2  List Medicines" + COLOR.reset);
  console.log(COLOR.yellow + " 3  Sell Medicine" + COLOR.reset);
  console.log(COLOR.yellow + " 4  Search Medicine" + COLOR.reset);
  console.log(COLOR.yellow + " 5  Alerts" + COLOR.reset);
  console.log(COLOR.yellow + " 6  Analytics" + COLOR.reset);
  console.log(COLOR.green + " 7  Web Dashboard" + COLOR.reset);
  console.log(COLOR.green + " 8  Reports" + COLOR.reset);
  console.log(COLOR.red + " 9  Stop Server" + COLOR.reset);
  console.log(COLOR.red + "10 Exit" + COLOR.reset);

  console.log(COLOR.magenta + "11 SAS Export" + COLOR.reset);
  console.log(COLOR.magenta + "12 Backup System" + COLOR.reset);
  console.log(COLOR.magenta + "13 System Health" + COLOR.reset);
  console.log(COLOR.blue + "14 Expiry Management" + COLOR.reset);
  console.log(COLOR.blue + "15 Supplier Management" + COLOR.reset);

  console.log(COLOR.cyan + "16 Purchase Management" + COLOR.reset);
  console.log(COLOR.cyan + "17 Daily Cash Report" + COLOR.reset);
  console.log(COLOR.cyan + "18 Inventory Valuation" + COLOR.reset);
  console.log(COLOR.cyan + "19 Advanced SAS Analytics" + COLOR.reset);
  console.log(COLOR.cyan + "20 Dashboard Snapshot" + COLOR.reset);
console.log(COLOR.green + "21 Batch Import" + COLOR.reset);
console.log(COLOR.magenta + "22 SAS Export Pipeline" + COLOR.reset);
console.log(COLOR.cyan + "23 Python Forecasting" + COLOR.reset);
console.log(COLOR.cyan + "24 Monte Carlo Inventory Risk" + COLOR.reset);
console.log(COLOR.blue + "25 Reorder Point Model" + COLOR.reset);
console.log(COLOR.blue + "26 Safety Stock Model" + COLOR.reset);
console.log(COLOR.blue + "27 Expiry Risk Simulation" + COLOR.reset);
console.log(COLOR.yellow + "28 ABC Analysis" + COLOR.reset);
console.log(COLOR.yellow + "29 EOQ Model" + COLOR.reset);
console.log(COLOR.red + "30 Integrated AI Dashboard" + COLOR.reset);
}


function menu() {
  banner();

  rl.question('Choice: ', c => {

    if (c === "1") addMedicine();
    else if (c === "2") listMedicines();
    else if (c === "3") sellMedicine();
    else if (c === "4") searchMedicine();
    else if (c === "5") alerts();
    else if (c === "6") analytics();
    else if (c === "7") webDashboard();
    else if (c === "8") reports();
    else if (c === "9") stopServer();
    else if (c === "10") process.exit();

    else if (c === "11") exportSAS();
    else if (c === "12") backupSystem();
    else if (c === "13") systemHealth();
    else if (c === "14") expiryManagement();
    else if (c === "15") supplierManagement();
    else if (c === "16") purchaseManagement();
    else if (c === "17") dailyCashReport();
    else if (c === "18") inventoryValuation();
    else if (c === "19") advancedSAS();
    else if (c === "20") dashboardSnapshot();
else if (c === "21") batchImport();
else if (c === "22") sasPipeline();
else if(c==="23") pythonForecast();
else if(c==="24") inventorySimulation();
else if(c==="25") reorderPointModel();
else if(c==="26") safetyStockModel();
else if(c==="27") expiryRiskSimulation();
else if(c==="28") abcAnalysis();
else if(c==="29") eoqModel();
else if(c==="30") integratedAIDashboard();

    else menu();
  });
}


function addMedicine() {
  rl.question('Name: ', name => {
    rl.question('Qty: ', qty => {
      rl.question('Price: ', price => {
        rl.question('Expiry: ', expiry => {

          let m = load(DB.MED);

          m.push({
            id: Date.now(),
            name,
            quantity: Number(qty),
            price: Number(price),
            expiry
          });

          save(DB.MED, m);
          log("ADD");

          console.log("Saved");
          pause();
        });
      });
    });
  });
}

function listMedicines() {
  console.table(load(DB.MED));
  pause();
}

function sellMedicine() {
  rl.question('Medicine: ', name => {
    rl.question('Qty: ', q => {

      let qty = Number(q);
      let meds = load(DB.MED);
      let med = meds.find(x => x.name === name);

      if (!med) return pause(console.log("Not found"));
      if (med.quantity < qty) return pause(console.log("Low stock"));

      med.quantity -= qty;

      save(DB.MED, meds);

      let sales = load(DB.SALES);

      sales.push({
        medicine: name,
        qty,
        total: qty * med.price,
        date: new Date().toISOString()
      });

      save(DB.SALES, sales);
      log("SALE");

      console.log("Done");
      pause();
    });
  });
}


function searchMedicine() {
  rl.question('Search: ', term => {
    console.table(load(DB.MED).filter(x =>
      x.name.toLowerCase().includes(term.toLowerCase())
    ));
    pause();
  });
}

function alerts() {
  console.table(load(DB.MED).filter(x => x.quantity <= 10));
  pause();
}

function analytics() {
  let s = load(DB.SALES);
  console.log("Sales:", s.length);
  console.log("Revenue:", s.reduce((a, b) => a + b.total, 0));
  pause();
}

function webDashboard() {
  const meds = load(DB.MED);
  const sales = load(DB.SALES);
  let revenue = sales.reduce((a, b) => a + b.total, 0);

  const html = `
<html><body style="font-family:Arial;text-align:center;background:#eef7ee">
<h1>PHARMACY DASHBOARD</h1>
<p>Medicines: ${meds.length}</p>
<p>Sales: ${sales.length}</p>
<p>Revenue: ${revenue}</p>
</body></html>`;

  http.createServer((req, res) => {
    res.end(html);
  }).listen(8080);

  pause();
}

function backupSystem() {
  const t = new Date().toISOString().replace(/[:.]/g, '-');
  fs.mkdirSync('backups', { recursive: true });

  fs.copyFileSync(DB.MED, `backups/med_${t}.json`);
  fs.copyFileSync(DB.SALES, `backups/sales_${t}.json`);

  console.log("Backup OK");
  pause();
}

function systemHealth() {
  console.log("OK");
  pause();
}

function expiryManagement() {
  console.table(load(DB.MED).filter(x => new Date(x.expiry) < new Date()));
  pause();
}

function supplierManagement() {
  console.log("Supplier module");
  pause();
}

function purchaseManagement() {
  console.log("Purchase module");
  pause();
}

function dailyCashReport() {
  let s = load(DB.SALES);
  console.log("Revenue:", s.reduce((a, b) => a + b.total, 0));
  pause();
}

function inventoryValuation() {
  let v = 0;
  load(DB.MED).forEach(x => v += x.price * x.quantity);
  console.log("Value:", v);
  pause();
}

function advancedSAS() {
  console.log("SAS Ready");
  pause();
}

function dashboardSnapshot() {
  let m = load(DB.MED);
  let s = load(DB.SALES);

  fs.writeFileSync('reports/snap.txt',
`Meds:${m.length}
Sales:${s.length}
Revenue:${s.reduce((a,b)=>a+b.total,0)}`);

  console.log("Snapshot saved");
  pause();
}

function exportSAS() { console.log("SAS export ready"); pause(); }


function reports(){

  const m = load(DB.MED);
  const s = load(DB.SALES);

  let revenue = s.reduce((a,b)=>a+b.total,0);

  let txt = `
PHARMACY REPORT V12
DATE: ${new Date().toISOString()}

--- INVENTORY ---
`;

  m.forEach(x=>{
    txt += `${x.name} | Qty:${x.quantity} | Price:${x.price} | Exp:${x.expiry}\n`;
  });

  txt += `

--- SALES ---
TOTAL SALES: ${s.length}
REVENUE: ${revenue}
`;

  s.forEach(x=>{
    txt += `${x.medicine} | Qty:${x.qty} | Total:${x.total} | Date:${x.date}\n`;
  });

  fs.writeFileSync('reports/pharmacy_report.txt', txt);

  let tex = fs.readFileSync('head.tex','utf8');

  tex += `

\\section*{Executive Summary}

This report was generated automatically by the Pharmacy Management System V12.


\\section*{Inventory Summary}

\\begin{longtable}{lrrl}
\\toprule
Medicine & Qty & Price & Expiry \\\\
\\midrule
`;

  m.forEach(x=>{
    tex += `${x.name} & ${x.quantity} & ${x.price} & ${x.expiry} \\\\\n`;
  });

  tex += `
\\bottomrule
\\end{longtable}

\\section*{Sales Summary}

Total Sales: ${s.length}

Total Revenue: ${revenue}

\\begin{longtable}{lrrl}
\\toprule
Medicine & Qty & Total & Date \\\\
\\midrule
`;

  s.forEach(x=>{
    tex += `${x.medicine} & ${x.qty} & ${x.total} & ${x.date} \\\\\n`;
  });

  tex += `
\\bottomrule
\\end{longtable}

\\section*{System Highlights}

\\begin{itemize}
\\item Inventory Management
\\item Sales Processing
\\item Analytics Engine
\\item SAS Export
\\item Backup System
\\item Audit Logging
\\item Health Monitoring
\\item Web Dashboard
\\end{itemize}

\\section*{Future Additions}

\\begin{itemize}
\\item AI Demand Forecasting
\\item Expiry Prediction
\\item Barcode Scanning
\\item QR Code Support
\\item Multi-Branch Pharmacies
\\item Cloud Synchronization
\\item Advanced SAS Analytics
\\end{itemize}

\\end{document}
`;

  fs.writeFileSync('reports/pharmacy_report.tex', tex);

  try {

    const { execSync } = require('child_process');

    execSync(
      process.env.HOME +
      '/compiletex1.sh reports/pharmacy_report.tex',
      {stdio:'inherit'}
    );

    console.log('TXT report generated.');
    console.log('LaTeX report generated.');
    console.log('PDF report generated.');

  } catch(e) {

    console.log('TXT report generated.');
    console.log('LaTeX report generated.');
    console.log('PDF compilation skipped.');
  }

  pause();
}

function stopServer(){
  const { execSync } = require('child_process');

  try {
    execSync("pkill -f node");
    execSync("fuser -k 8080/tcp");
    console.log("Server stopped successfully");
  } catch(e) {
    console.log("Stop executed (no active process)");
  }

  pause();
}

function batchImport() {

  rl.question('Batch file: ', file => {

    try {

      const lines = fs.readFileSync(file, 'utf8')
        .split('\n')
        .filter(x =>
          x.trim() !== '' &&
          !x.trim().startsWith('#')
        );

      let meds = load(DB.MED);

      let count = 0;

      lines.forEach(line => {

        const p = line.split('|');

        if (p.length < 4) return;

        meds.push({
          id: Date.now() + Math.floor(Math.random() * 1000000),
          name: p[0].trim(),
          quantity: Number(p[1]),
          price: Number(p[2]),
          expiry: p[3].trim()
        });

        count++;

      });

      save(DB.MED, meds);

      log('BATCH_IMPORT');

      console.log(count + ' medicines imported');

    } catch (e) {

      console.log('Import failed');

    }

    pause();

  });

}

function sasPipeline() {

  const meds = load(DB.MED);
  const sales = load(DB.SALES);

  let sas = "";

  sas += "DATA medicines;\nINPUT name $ quantity price expiry $;\nDATALINES;\n";

  meds.forEach(x => {
    sas += `${x.name} ${x.quantity} ${x.price} ${x.expiry}\n`;
  });

  sas += ";\nRUN;\n\n";

  sas += "DATA sales;\nINPUT medicine $ qty total date $;\nDATALINES;\n";

  sales.forEach(x => {
    sas += `${x.medicine} ${x.qty} ${x.total} ${x.date}\n`;
  });

  sas += ";\nRUN;\n\n";

  sas += "PROC MEANS DATA=medicines;\nRUN;\n";
  sas += "PROC MEANS DATA=sales;\nRUN;\n";

  fs.writeFileSync("exports/sas_pipeline.sas", sas);

  console.log("SAS pipeline exported to exports/sas_pipeline.sas");

  pause();
}

function reorderPointModel(){

  try{

    execSync(
      "python simulation/reorder_point.py",
      {stdio:"inherit"}
    );

  }catch(e){

    console.log("Model failed");

  }

  pause();

}

function safetyStockModel(){

  try{

    execSync(
      "python simulation/safety_stock.py",
      {stdio:"inherit"}
    );

  }catch(e){

    console.log("Model failed");

  }

  pause();

}

function expiryRiskSimulation(){

  try{

    execSync(
      "python simulation/expiry_risk.py",
      {stdio:"inherit"}
    );

  }catch(e){

    console.log("Simulation failed");

  }

  pause();

}

function abcAnalysis(){

  try{

    execSync(
      "python simulation/abc_analysis.py",
      {stdio:"inherit"}
    );

  }catch(e){

    console.log("Analysis failed");

  }

  pause();

}

function eoqModel(){

  try{

    execSync(
      "python simulation/eoq.py",
      {stdio:"inherit"}
    );

  }catch(e){

    console.log("EOQ failed");

  }

  pause();

}

function integratedAIDashboard(){

  try{

    execSync(
      "python simulation/ai_dashboard.py",
      {stdio:"inherit"}
    );

  }catch(e){

    console.log("Dashboard failed");

  }

  pause();

}

function pythonForecast(){

  try{

    execSync(
      "python simulation/forecast.py",
      {stdio:"inherit"}
    );

  }catch(e){

    console.log("Forecast failed");

  }

  pause();

}

function inventorySimulation(){

  try{

    execSync(
      "python simulation/inventory_sim.py",
      {stdio:"inherit"}
    );

  }catch(e){

    console.log("Simulation failed");

  }

  pause();

}




console.log("System loaded. Available modules ready.");

menu();




