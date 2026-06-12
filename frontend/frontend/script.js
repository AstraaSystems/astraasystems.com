async function runEstimate() {
  const data = await estimate({
    sqft: 10000,
    material: 1.1,
    labor: 1.05,
    complexity: 0.8
  });

  document.getElementById("result").innerHTML =
    "Estimate: $" + Math.round(data.base_estimate);
}
