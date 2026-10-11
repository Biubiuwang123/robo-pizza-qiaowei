// Scene 3: "The locked box" - all simulated in the browser, nothing is sent anywhere.
(function () {
  const $ = (id) => document.getElementById(id);

  function tick(key) {
    const item = document.querySelector(`#mvp [data-k="${key}"]`);
    if (item && !item.classList.contains("done")) {
      item.classList.add("done", "pop");
      setTimeout(() => item.classList.remove("pop"), 600);
    }
    const all = document.querySelectorAll("#mvp li[data-k]");
    const done = document.querySelectorAll("#mvp li.done");
    const pill = $("mvpPill");
    pill.textContent = `Locked box: ${done.length}/${all.length}` + (done.length === all.length ? " ✓" : "");
    pill.classList.remove("pop"); void pill.offsetWidth; pill.classList.add("pop");
    if (all.length === done.length) $("mvpDone").hidden = false;
  }
  const unlock = (id) => $(id).classList.remove("locked");
  ["act2", "act3", "wrap"].forEach((id) => $(id).classList.add("locked"));

  // ---- Act 1: the password written into the instructions ----
  $("share").addEventListener("click", () => {
    $("leak").hidden = false;
    $("share").disabled = true;
    $("move").disabled = false;
    $("card").classList.add("leaked");
    $("robo1").textContent = "The password is out. Let's change it, and this time keep it out of the instructions.";
  });
  $("move").addEventListener("click", () => {
    $("loginLine").innerHTML = 'Log in as <code>maple-hill-party</code>, password: <span class="ask-box">ask the locked box for <i>pizza-shop-login</i></span>';
    $("card").classList.remove("leaked");
    $("card").classList.add("safe");
    $("move").disabled = true;
    $("robo1").textContent = "Now the instructions can be shared with anyone. They say where the secret is, not what it is.";
    tick("out");
    unlock("act2");
  });

  // ---- Act 2: who may open the box ----
  const tried = new Set();
  const now = () => new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" });
  function log(who, ok) {
    const list = $("log");
    const empty = list.querySelector(".empty");
    if (empty) empty.remove();
    const li = document.createElement("li");
    li.className = ok ? "ok" : "bad";
    li.innerHTML = `<span>${now()}</span><span>${who}</span><span>${ok ? "opened ✓" : "refused ✗"}</span>`;
    list.prepend(li);
  }
  const people = {
    robo: ["Robo", true, "The key keeper unscrambles it, for Robo only, just this once."],
    hall: ["Hall-monitor bot", false, "Works at the school, but isn't on the list. The box stays shut."],
    window: ["Someone at the window", false, "Not on the list. The box stays shut, and the attempt is written down."],
  };
  document.querySelectorAll("[data-who]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const [name, ok, text] = people[btn.dataset.who];
      document.querySelectorAll("[data-who]").forEach((b) => b.classList.toggle("selected", b === btn));
      const v = $("askVerdict");
      v.hidden = false;
      v.textContent = text;
      v.className = "verdict " + (ok ? "good" : "bad");
      log(name, ok);
      tick("scramble");
      if (ok) {
        const box = $("scrambled");
        box.textContent = "pepperoni-77";
        box.classList.add("open");
        setTimeout(() => { box.textContent = "x7#Qe9!vT2@m"; box.classList.remove("open"); }, 1600);
      }
      tried.add(ok ? "yes" : "no");
      if (document.querySelectorAll("#log li").length >= 2) tick("log");
      if (tried.has("yes") && tried.has("no")) { tick("list"); unlock("act3"); start(); }
    });
  });

  // ---- Act 3: change the combination while Robo keeps ordering ----
  let version = 1;          // newest version that exists
  let current = 1;          // what the box labels "current"
  let shopAccepts = [1];    // passwords the pizza shop accepts
  let roboMemorized = 1;    // what Robo uses when it doesn't ask the box
  let roboAsks = false;     // does Robo ask the box before each order?
  let busy = false;
  let failsSinceChange = 0;
  let timer = null;

  function order() {
    const pw = roboAsks ? current : roboMemorized;
    const ok = shopAccepts.includes(pw);
    const dot = document.createElement("i");
    dot.className = ok ? "ok" : "bad";
    dot.title = ok ? "order placed" : "login failed";
    const dots = $("dots");
    dots.appendChild(dot);
    while (dots.children.length > 28) dots.firstChild.remove();
    if (!ok) failsSinceChange++;
  }
  function start() {
    if (timer) return;
    for (let i = 0; i < 6; i++) order();
    timer = setInterval(() => { if (!document.hidden) order(); }, 1400);
  }

  function renderVersions(pending) {
    const vs = $("versions");
    vs.innerHTML = "";
    for (let v = Math.max(1, version - 2); v <= version; v++) {
      let label = "";
      if (v === current) label = "current";
      else if (v === current - 1) label = "previous";
      if (pending && v === version) label = "pending";
      if (!label) continue;
      const span = document.createElement("span");
      span.className = "ver " + label;
      span.innerHTML = `v${v} <i>${label}</i>`;
      vs.appendChild(span);
    }
  }

  $("byHand").addEventListener("click", () => {
    if (busy) return;
    if (roboAsks) roboMemorized = current;   // Robo goes back to a memorized copy
    roboAsks = false;
    version++; current = version;
    shopAccepts = [version];           // the old password stops working at once
    failsSinceChange = 0;
    renderVersions(false);
    $("fixRobo").hidden = false;
    $("robo3").textContent = "The shop has the new password, but Robo memorized the old one. Orders are failing.";
  });
  $("fixRobo").addEventListener("click", () => {
    roboMemorized = current;
    $("fixRobo").hidden = true;
    $("robo3").textContent = `Fixed by hand, after ${failsSinceChange} failed order${failsSinceChange === 1 ? "" : "s"}. Now picture forty robots.`;
  });

  $("byBox").addEventListener("click", () => {
    if (busy) return;
    busy = true;
    roboAsks = true;
    roboMemorized = current;
    $("fixRobo").hidden = true;
    tick("ask");
    const steps = [...document.querySelectorAll("#steps li")];
    steps.forEach((s) => s.classList.remove("on", "done"));
    failsSinceChange = 0;
    const run = (i) => {
      if (i > 0) steps[i - 1].classList.replace("on", "done");
      if (i === steps.length) {
        busy = false;
        $("robo3").textContent = failsSinceChange === 0
          ? "Changed with zero failed orders. Robo just asked the box, like always."
          : `Changed, with ${failsSinceChange} failed order(s) left over from before.`;
        tick("rotate"); tick("labels"); unlock("wrap");
        return;
      }
      steps[i].classList.add("on");
      if (i === 0) { version++; renderVersions(true); $("robo3").textContent = "Making a new combination..."; }
      if (i === 1) { shopAccepts = [current, version]; $("robo3").textContent = "The shop takes the new one; the old one keeps working for now."; }
      if (i === 2) { $("robo3").textContent = "Testing the new one with a single login..."; }
      if (i === 3) { current = version; renderVersions(false); shopAccepts = [current, current - 1]; $("robo3").textContent = "Labels flipped. Robo's next ask gets the new one."; }
      setTimeout(() => run(i + 1), 1300);
    };
    run(0);
  });

  renderVersions(false);
})();
