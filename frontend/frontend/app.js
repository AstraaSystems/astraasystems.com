import { hero } from "./components/hero.js";
import { privacy } from "./components/privacy.js";
import { features } from "./components/features.js";
import { estimator } from "./components/estimator.js";
import { contact } from "./components/contact.js";
import { support } from "./components/support.js";

const app = document.getElementById("app");

app.innerHTML = `
  ${hero()}
  ${privacy()}
  ${features()}
  ${estimator()}
  ${contact()}
  ${support()}
`;
