// Scene 2: "Is that badge real?" - all simulated in the browser, nothing is sent anywhere.
(function () {
  const $ = (id) => document.getElementById(id);

  // ---- The minimum badge office checklist ----
  function tick(key) {
    const item = document.querySelector(`#mvp [data-k="${key}"]`);
    if (item && !item.classList.contains("done")) {
      item.classList.add("done");
      item.classList.add("pop");
      setTimeout(() => item.classList.remove("pop"), 600);
    }
    const all = document.querySelectorAll("#mvp li[data-k]");
    const done = document.querySelectorAll("#mvp li.done");
    const pill = $("mvpPill");
    pill.textContent = `Badge office: ${done.length}/${all.length}` + (done.length === all.length ? " ✓" : "");
    pill.classList.remove("pop"); void pill.offsetWidth; pill.classList.add("pop");
    if (all.length === done.length) $("mvpDone").hidden = false;
  }
  function unlock(id) { $(id).classList.remove("locked"); }

  // Acts after the first start locked until the previous step is played.
  ["act2", "act3", "act4", "act5", "act6", "act7", "wrap"].forEach((id) => $(id).classList.add("locked"));

  // ---- Act 1: inspect the real badge ----
  $("lock1").addEventListener("click", () => {
    $("badge1").hidden = false;
    $("lock1").classList.add("active");
    $("robo1").textContent = "All four checks pass. Safe to sign in.";
    ["who", "vouch", "seal"].forEach(tick);
    unlock("act2");
  });

  // ---- Act 2: two impostors ----
  document.querySelectorAll(".btn-choice").forEach((btn) => {
    btn.addEventListener("click", () => {
      const which = btn.dataset.imp;
      document.querySelectorAll(".btn-choice").forEach((b) => b.classList.toggle("selected", b === btn));
      $("impA").hidden = which !== "a";
      $("impB").hidden = which !== "b";
    });
  });

  $("runChallenge").addEventListener("click", () => {
    const li = $("challenge");
    const mark = li.querySelector(".mark");
    $("nonce").textContent = String(Math.floor(10000 + Math.random() * 89999));
    $("runChallenge").disabled = true;
    mark.textContent = "…";
    setTimeout(() => {
      mark.textContent = "✗";
      $("verdictB").hidden = false;
      tick("key");
      unlock("act3");
    }, 900);
  });

  // ---- Act 3: earn a badge by pinning a note on your own door ----
  $("impostorAsk").addEventListener("click", () => {
    $("office").innerHTML = "Impostor B asks for a party.maplehill.example badge... but it can't reach <b>your</b> door, so there's no note. <span class=\"no\">Refused ✗</span>";
  });
  $("pinNote").addEventListener("click", () => {
    $("note").hidden = false;
    $("door").classList.add("pinned");
    $("pinNote").disabled = true;
    $("office").textContent = "Checking the door...";
    setTimeout(() => {
      $("office").innerHTML = "Found the note. Here's your badge, stamped by Trusty Stamps. <span class=\"yes\">Issued ✓</span>";
      tick("own");
      unlock("act4");
      draw();
    }, 1100);
  });

  // ---- Act 4: fast-forward time ----
  const HORIZON = 400;

  function simulate() {
    const life = $("rules2029").checked ? 47 : 198;
    const renewBefore = life === 198 ? 45 : 11; // re-stamp 45 days early today; proportionally earlier under 47-day rules
    const canRenew = $("autoRenew").checked && $("noteStays").checked;
    const badges = [];   // [start, end)
    let start = 0;
    let failedAt = null;
    while (start < HORIZON) {
      const end = start + life;
      badges.push([start, end]);
      const renewAt = end - renewBefore;
      if (renewAt >= HORIZON) break;
      if (!canRenew) { failedAt = $("autoRenew").checked ? renewAt : null; break; }
      start = renewAt;
    }
    const lastEnd = badges[badges.length - 1][1];
    return { life, renewBefore, badges, renewals: badges.length - 1, downFrom: lastEnd < HORIZON ? lastEnd : null, failedAt };
  }

  function draw() {
    const sim = simulate();
    const tl = $("timeline");
    tl.innerHTML = "";
    const pct = (d) => `${(Math.min(d, HORIZON) / HORIZON) * 100}%`;
    const valid = document.createElement("div");
    valid.className = "seg valid";
    valid.style.left = "0";
    valid.style.width = pct(sim.downFrom ?? HORIZON);
    tl.appendChild(valid);
    if (sim.downFrom !== null) {
      const down = document.createElement("div");
      down.className = "seg down";
      down.style.left = pct(sim.downFrom);
      down.style.width = pct(HORIZON - sim.downFrom);
      tl.appendChild(down);
    }
    sim.badges.slice(1).forEach(([s]) => {
      const m = document.createElement("div");
      m.className = "renew-mark";
      m.style.left = pct(s);
      tl.appendChild(m);
    });
    const cursor = document.createElement("div");
    cursor.className = "cursor";
    cursor.style.left = pct(+$("days").value);
    tl.appendChild(cursor);
    update(sim);
  }

  function update(sim) {
    const day = +$("days").value;
    $("dayOut").textContent = day;
    const down = sim.downFrom !== null && day >= sim.downFrom;
    const renewalsSoFar = sim.badges.slice(1).filter(([s]) => s <= day).length;
    $("mini").classList.toggle("down", down);
    $("miniLock").textContent = down ? "⚠️" : "🔒";
    $("miniText").textContent = down ? "Not secure: this site's badge expired" : "party.maplehill.example";

    let msg;
    if (down && sim.failedAt !== null) msg = "Re-stamping failed: the note wasn't on the door anymore. No pizza.";
    else if (down) msg = "Nobody re-stamped the badge. Browsers block the site. No pizza.";
    else if (renewalsSoFar > 0) msg = `Re-stamped ${renewalsSoFar} time${renewalsSoFar > 1 ? "s" : ""} so far, ${sim.renewBefore} days before each expiry. Nobody had to remember.`;
    else if (day === 0) msg = "Drag the slider.";
    else msg = `Badge good for ${sim.life - day} more days.`;
    $("robo4").textContent = msg;

    $("stats").textContent = sim.downFrom === null
      ? `Over ${HORIZON} days: ${sim.renewals} automatic re-stamps, 0 days down.`
      : `Over ${HORIZON} days: site down from day ${sim.downFrom}.`;

    if (day >= sim.life - sim.renewBefore) tick("expire");
    if (renewalsSoFar > 0 && sim.downFrom === null) { tick("renew"); unlock("act5"); }
  }

  // ---- Act 5: build the school's private badge office ----
  $("mkMaster").addEventListener("click", () => {
    $("cMaster").hidden = false; $("mkMaster").disabled = true; $("mkDesk").disabled = false; tick("master");
  });
  $("mkDesk").addEventListener("click", () => {
    $("cDesk").hidden = false; $("mkDesk").disabled = true; $("mkBadge").disabled = false; tick("desk");
  });
  $("mkBadge").addEventListener("click", () => {
    $("cBadge").hidden = false; $("mkBadge").disabled = true; unlock("act6");
  });

  // ---- Act 6: both sides check each other ----
  function handshake(visitorOk) {
    $("handshake").hidden = false;
    const m1 = $("hs1").querySelector(".hs-msg"), m2 = $("hs2").querySelector(".hs-msg");
    const v = $("hsVerdict");
    m1.textContent = "…"; m2.textContent = ""; v.textContent = ""; v.className = "verdict";
    $("hs1").className = "hs-row"; $("hs2").className = "hs-row";
    setTimeout(() => {
      m2.textContent = "kitchen.school.example, stamped by Maple Hill ✓";
      $("hs2").classList.add("ok");
    }, 500);
    setTimeout(() => {
      if (visitorOk) {
        m1.textContent = "robo.school.example, stamped by Maple Hill ✓";
        $("hs1").classList.add("ok");
        v.textContent = "Both badges check out. \"Come in.\"";
        v.classList.add("good");
      } else {
        m1.textContent = "drone.delivery.example, stamped by Somewhere Else ✗";
        $("hs1").classList.add("bad");
        v.textContent = "A real badge, but not one of ours. Door stays shut.";
        v.classList.add("bad");
        tick("trust");
        unlock("act7");
      }
    }, 1000);
  }
  $("knockRobo").addEventListener("click", () => handshake(true));
  $("knockDrone").addEventListener("click", () => handshake(false));

  // ---- Act 7: cancel a badge whose key was copied ----
  let revoked = false;
  $("longLife").addEventListener("change", () => {
    $("risk").innerHTML = $("longLife").checked
      ? "The copy works for up to <b>a whole year</b> unless someone cancels it."
      : "The copy works for at most <b>1 day</b>, even if nobody notices.";
  });
  $("revoke").addEventListener("click", () => {
    revoked = true; $("cancelled").hidden = false; $("revoke").disabled = true;
  });
  $("thief").addEventListener("click", () => {
    const v = $("thiefVerdict");
    v.hidden = false;
    if (revoked) {
      v.textContent = "Kitchen checks the cancelled list: this badge was cancelled. Door stays shut. Robo gets a fresh badge with a new key.";
      v.className = "verdict good";
      tick("revoke");
      unlock("wrap");
    } else {
      v.textContent = "Badge and key both check out, so the thief walks in. Cancel the badge first.";
      v.className = "verdict bad";
    }
  });

  ["autoRenew", "noteStays", "rules2029"].forEach((id) => $(id).addEventListener("change", draw));
  $("days").addEventListener("input", draw);
  draw();
})();
