
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

Handler

else if(c==="21") batchImport();
else if(c==="22") sasPipeline();
else if(c==="23") pythonForecast();
else if(c==="24") inventorySimulation();
else if(c==="25") reorderPointModel();
else if(c==="26") safetyStockModel();
else if(c==="27") expiryRiskSimulation();
else if(c==="28") abcAnalysis();
else if(c==="29") eoqModel();
else if(c==="30") integratedAIDashboard();

Functions

function reorderPointModel(){

  try{

    execSync(
      "python reorder_point.py",
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
      "python safety_stock.py",
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
      "python expiry_risk.py",
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
      "python abc_analysis.py",
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
      "python eoq.py",
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
      "python ai_dashboard.py",
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
      "python forecast.py",
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
      "python inventory_sim.py",
      {stdio:"inherit"}
    );

  }catch(e){

    console.log("Simulation failed");

  }

  pause();

}



