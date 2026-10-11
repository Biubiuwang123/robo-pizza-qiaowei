// Scene 4: "The staff roster" - all simulated in the browser, nothing is sent anywhere.
(function () {
  // Acts unlock in order as the reader plays; see scene-kit.js.
  const { $, tick, unlock } = SceneKit.start({
    pillLabel: "Staff roster",
    locked: ["act2", "act3", "act4", "act5", "wrap"],
  });

  const SYSTEMS = [
    { name: "Classroom computers", icon: "🖥️", group: "Teachers" },
    { name: "Library", icon: "📚", group: "Teachers" },
    { name: "Copy machine", icon: "🖨️", group: "Teachers" },
    { name: "School Wi-Fi", icon: "📶", group: "Teachers" },
    { name: "Shared files", icon: "📁", group: "Teachers" },
    { name: "Pizza account", icon: "🍕", group: "Party committee" },
  ];
  const EVERYDAY = SYSTEMS.slice(0, 5);

  // Draw a row of system tiles. `state(sys, i)` returns [cssState, label, buttonText?].
  function draw(container, systems, state, onButton) {
    container.innerHTML = "";
    systems.forEach((sys, i) => {
      const [cls, label, button] = state(sys, i);
      const tile = document.createElement("div");
      tile.className = `sys ${cls}`;
      tile.innerHTML = `<span class="sys-icon" aria-hidden="true">${sys.icon}</span><b>${sys.name}</b><span class="sys-state">${label}</span>`;
      if (button) {
        const b = document.createElement("button");
        b.className = "btn-small ghost";
        b.textContent = button;
        b.addEventListener("click", () => onButton(i));
        tile.appendChild(b);
      }
      container.appendChild(tile);
    });
  }
  function setMode(onId, offId) { $(onId).classList.add("on"); $(offId).classList.remove("on"); }

  // ---- Act 1: add a new teacher, list by list or once ----
  let added = new Set();
  function drawManual() {
    draw($("sys1"), EVERYDAY,
      (s, i) => added.has(i) ? ["ok", "has his own account here"] : ["pending", "doesn't know him", "Add Mr. Okafor"],
      (i) => {
        added.add(i);
        drawManual();
        $("robo1").textContent = added.size < EVERYDAY.length
          ? `${added.size} of ${EVERYDAY.length} lists done. Each one also gave him a separate password to remember.`
          : `Done, after ${EVERYDAY.length} separate sign-ups and ${EVERYDAY.length} passwords. Now try it with a roster.`;
      });
  }
  $("mode1A").addEventListener("click", () => {
    setMode("mode1A", "mode1B"); $("rosterAddRow").hidden = true; added = new Set(); drawManual();
    $("robo1").textContent = "Without a roster, every system keeps its own list. Add him to each one.";
  });
  $("mode1B").addEventListener("click", () => {
    setMode("mode1B", "mode1A"); $("rosterAddRow").hidden = false; $("rosterAdd").disabled = false;
    draw($("sys1"), EVERYDAY, () => ["pending", "asks the roster"]);
    $("robo1").textContent = "With a roster, the systems keep no lists of their own. They ask.";
  });
  $("rosterAdd").addEventListener("click", () => {
    $("rosterAdd").disabled = true;
    draw($("sys1"), EVERYDAY, () => ["ok", "roster says: yes, a teacher"]);
    $("robo1").textContent = "One entry, one password, and every system knows him at once.";
    tick("one");
    unlock("act2");
  });
  drawManual();

  // ---- Act 2: systems grant groups; the roster answers who's in them ----
  function drawGroups() {
    const inParty = $("gParty").checked;
    draw($("sys2"), SYSTEMS, (s) => {
      const yes = s.group === "Teachers" || inParty;
      return [yes ? "ok" : "no", `allows group "${s.group}"`];
    });
    $("askAnswer").textContent = inParty ? "yes" : "no";
    $("askAnswer").className = inParty ? "yes" : "no";
  }
  $("gParty").addEventListener("change", () => {
    drawGroups();
    tick("groups"); tick("lookup");
    if ($("gParty").checked) unlock("act3");
  });
  drawGroups();

  // ---- Act 3: remove someone, list by list or once ----
  let rosterMode3 = false;
  const FORGOTTEN = new Set(["Copy machine", "School Wi-Fi"]);
  function drawChen(phase) {
    draw($("sys3"), SYSTEMS, (s) => {
      if (phase === "before") return ["ok", "Ms. Chen can get in"];
      if (rosterMode3) return ["locked", "roster says: not here anymore"];
      if (FORGOTTEN.has(s.name)) return [phase === "september" ? "orphan" : "ok", phase === "september" ? "still opens for Ms. Chen!" : "the office forgot this one"];
      return ["locked", "removed by hand"];
    });
  }
  function resetAct3() {
    $("chenLeaves").disabled = false; $("september").hidden = true; $("leaveVerdict").hidden = true; drawChen("before");
  }
  $("mode3A").addEventListener("click", () => { setMode("mode3A", "mode3B"); rosterMode3 = false; resetAct3(); });
  $("mode3B").addEventListener("click", () => { setMode("mode3B", "mode3A"); rosterMode3 = true; resetAct3(); });
  $("chenLeaves").addEventListener("click", () => {
    $("chenLeaves").disabled = true;
    drawChen("june");
    const v = $("leaveVerdict");
    v.hidden = false;
    if (rosterMode3) {
      v.textContent = "One switch in the roster, and all six systems refuse her the same minute.";
      v.className = "verdict good";
      tick("remove");
      unlock("act4");
    } else {
      v.textContent = "The office worked through the lists in June and missed two.";
      v.className = "verdict bad";
      $("september").hidden = false;
    }
  });
  $("september").addEventListener("click", () => {
    $("september").hidden = true;
    drawChen("september");
    $("leaveVerdict").textContent = "September: Ms. Chen's old account still opens the copy machine and the Wi-Fi. Nobody noticed. Try it with a roster.";
  });
  drawChen("before");

  // ---- Act 4: one sign-in, a ticket for the day ----
  const visited = new Set();
  $("morning").addEventListener("click", () => {
    $("morning").disabled = true;
    $("ticket").hidden = false;
    $("visits").hidden = false;
  });
  document.querySelectorAll("[data-visit]").forEach((btn) => {
    btn.addEventListener("click", () => {
      document.querySelectorAll("[data-visit]").forEach((b) => b.classList.toggle("selected", b === btn));
      visited.add(btn.dataset.visit);
      const v = $("visitVerdict");
      v.hidden = false;
      v.textContent = `${btn.dataset.visit}: shows the day ticket, the roster's seal checks out. In, without typing her password again.`;
      v.className = "verdict good";
      if (visited.size >= 2) { tick("ticket"); unlock("act5"); }
    });
  });

  // ---- Act 5: survive a power cut with a second copy ----
  $("secondCopy").addEventListener("change", () => {
    const on = $("secondCopy").checked;
    $("bGym").classList.toggle("off", !on);
    $("bGym").querySelector("span").textContent = on ? "roster copy 2, kept in sync" : "no copy";
  });
  $("powerCut").addEventListener("click", () => {
    $("powerCut").disabled = true;
    $("bMain").classList.add("down");
    const v = $("powerVerdict");
    v.hidden = false;
    if ($("secondCopy").checked) {
      v.textContent = "The main building goes dark, and the gym's copy keeps answering. Nobody notices.";
      v.className = "verdict good";
      tick("copies");
      unlock("wrap");
    } else {
      v.textContent = "The only roster is in the dark. Nobody at Maple Hill can sign in to anything until the power is back.";
      v.className = "verdict bad";
    }
    setTimeout(() => { $("bMain").classList.remove("down"); $("powerCut").disabled = false; }, 2500);
  });
})();
