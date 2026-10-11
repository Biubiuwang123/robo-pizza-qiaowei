// Scene 1: "Who's at the door?" - all simulated in the browser, nothing is sent anywhere.
(function () {
  // Acts unlock in order as the reader plays; see scene-kit.js.
  const { $, tick, unlock } = SceneKit.start({
    pillLabel: "Sign-in desk",
    locked: ["act2", "act3", "act4", "wrap"],
  });

  const STRONG = "class-party-pepperoni-7";
  const b64url = (obj) => btoa(JSON.stringify(obj)).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
  const SEAL = "kQ3vZr8fT1xWm0bN7yLcA2sHuE5dGpJ4oV9iR6tY";

  // ---- Act 1: sign up, verify the email, see what the desk keeps ----
  $("pwWeak").addEventListener("click", () => {
    $("pw").value = "pizza1";
    $("signUp").disabled = false;
    $("pwVerdict").hidden = true;
  });
  $("pwStrong").addEventListener("click", () => {
    $("pw").value = STRONG;
    $("signUp").disabled = false;
    $("pwVerdict").hidden = true;
  });
  $("signUp").addEventListener("click", () => {
    const v = $("pwVerdict");
    v.hidden = false;
    if ($("pw").value.length < 12) {
      v.textContent = "Too short. The desk wants at least 12 characters and a number.";
      v.className = "verdict bad";
      return;
    }
    v.textContent = "Accepted. Now prove the email is really hers.";
    v.className = "verdict good";
    $("signUp").disabled = true;
    $("mail").hidden = false;
    $("robo1").textContent = "The desk just sent a code to her inbox. Only someone who can read it can finish signing up.";
  });
  $("enterCode").addEventListener("click", async () => {
    $("enterCode").disabled = true;
    $("ledger").hidden = false;
    tick("verify");
    // A real SHA-256 of salt + password, computed in your browser, to show what a fingerprint looks like.
    const salt = "9f2c41d7";
    let shown = "sha256:" + salt + "$…";
    if (window.crypto && crypto.subtle) {
      const digest = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(salt + $("pw").value));
      shown = "sha256:" + salt + "$" + [...new Uint8Array(digest)].slice(0, 12).map((b) => b.toString(16).padStart(2, "0")).join("") + "…";
    }
    $("fingerprint").textContent = shown;
    $("robo1").textContent = "Even the desk can't read her password back. At sign-in it fingerprints what she types and compares.";
    tick("hash");
    unlock("act2");
  });

  // ---- Act 2: wristbands and rooms that check the seal alone ----
  const now = Math.floor(Date.now() / 1000);
  const header = { alg: "RS256", kid: "desk-key-1", typ: "JWT" };
  function payload(may, issuedAt) {
    return { sub: "a1f3-rivera", email: "ms.rivera@maplehill.example", may, iat: issuedAt, exp: issuedAt + 3600 };
  }
  let band = { may: "order pizza, see the class list", iat: now, sealedMay: "order pizza, see the class list", sealedIat: now };

  function showJwt() {
    const p = payload(band.may, band.iat);
    $("jH").textContent = b64url(header).slice(0, 16) + "…";
    $("jP").textContent = b64url(p).slice(0, 26) + "…";
    $("jS").textContent = SEAL.slice(0, 14) + "…";
    $("jHd").textContent = JSON.stringify(header, null, 1);
    $("jPd").textContent = JSON.stringify({ email: p.email, may: p.may, exp: "in 1 hour" }, null, 1);
  }

  $("signIn").addEventListener("click", () => {
    $("signIn").disabled = true;
    $("bands").hidden = false;
    $("jwt").hidden = false;
    $("rooms").hidden = false;
    showJwt();
    tick("band");
  });
  $("bandId").addEventListener("click", () => $("jwt").scrollIntoView({ behavior: "smooth", block: "nearest" }));
  $("bandAccess").addEventListener("click", () => $("jwt").scrollIntoView({ behavior: "smooth", block: "nearest" }));

  // The seal matches only if the contents are exactly what the desk signed.
  const sealOk = () => band.may === band.sealedMay && band.iat === band.sealedIat;
  let clock = now;
  const expired = () => clock >= band.iat + 3600;

  function checkAt(room) {
    if (!sealOk()) return [false, "The seal doesn't match the contents. Someone changed this wristband. Refused."];
    if (expired()) return [false, "The seal is fine, but this wristband ran out. Refused."];
    if (room === "pizza" && !band.may.includes("order pizza") && band.may !== "everything") return [false, "Not allowed to order pizza."];
    return [true, room === "party"
      ? "Seal checks out against the desk's public pattern: this is Ms. Rivera. Welcome."
      : "Seal checks out, and the band says she may order pizza. Go ahead."];
  }
  const roomsSeen = new Set();
  document.querySelectorAll("[data-room]").forEach((btn) => {
    btn.addEventListener("click", () => {
      document.querySelectorAll("[data-room]").forEach((b) => b.classList.toggle("selected", b === btn));
      const [ok, text] = checkAt(btn.dataset.room);
      const v = $("roomVerdict");
      v.hidden = false; v.textContent = text; v.className = "verdict " + (ok ? "good" : "bad");
      if (ok) roomsSeen.add(btn.dataset.room);
      if (roomsSeen.size === 2) { tick("seal"); unlock("act3"); }
    });
  });

  // ---- Act 3: edit it, or let it run out ----
  $("mayEdit").addEventListener("change", () => { band.may = $("mayEdit").value; showJwt(); });
  $("showEdited").addEventListener("click", () => {
    const [ok, text] = checkAt("pizza");
    const v = $("editVerdict");
    v.hidden = false; v.textContent = text; v.className = "verdict " + (ok ? "good" : "bad");
    if (!sealOk()) $("editVerdict").textContent += " Any change, even one letter, breaks the seal.";
  });
  $("fastForward").addEventListener("click", () => {
    band.may = band.sealedMay; $("mayEdit").value = band.sealedMay; showJwt();
    clock = band.iat + 3601;
    const [, text] = checkAt("pizza");
    const v = $("timeVerdict");
    v.hidden = false; v.textContent = text; v.className = "verdict bad";
    $("useRefresh").hidden = false;
    $("fastForward").disabled = true;
  });
  $("useRefresh").addEventListener("click", () => {
    band.iat = clock; band.sealedIat = clock;   // the desk seals a fresh band
    showJwt();
    const v = $("timeVerdict");
    v.textContent = "The pocket band got her a fresh wristband for another hour. She never retyped her password.";
    v.className = "verdict good";
    $("useRefresh").hidden = true;
    tick("expire");
    unlock("act4");
  });

  // ---- Act 4: a guesser, a lockout, and a second proof ----
  let tries = 0;
  const LIMIT = 5;
  $("guess").addEventListener("click", () => {
    $("guess").disabled = true;
    const list = $("guesses");
    const guesses = ["pizza123", "maplehill1", "rivera2026", "password!", "teacher99", "party2026", "letmein42"];
    const step = () => {
      if (tries >= guesses.length) return done();
      tries++;
      const li = document.createElement("li");
      li.innerHTML = tries <= LIMIT
        ? `<code>${guesses[tries - 1]}</code> <span>wrong password</span>`
        : `<code>${guesses[tries - 1]}</code> <span class="lock-msg">too many tries, wait</span>`;
      list.appendChild(li);
      setTimeout(step, 380);
    };
    const done = () => {
      const v = $("guessVerdict");
      v.hidden = false;
      v.textContent = `After ${LIMIT} wrong guesses the desk stops checking for a while. Guessing becomes painfully slow.`;
      v.className = "verdict good";
      tick("slow");
      $("leakedBox").hidden = false;
    };
    step();
  });
  $("realPw").addEventListener("click", () => {
    const v = $("mfaVerdict");
    v.hidden = false;
    if ($("mfa").checked) {
      v.textContent = "Right password, but the desk now wants the code from Ms. Rivera's phone. The guesser doesn't have it. Stuck at the door.";
      v.className = "verdict good";
      tick("mfa");
      unlock("wrap");
    } else {
      v.textContent = "With only a password, the right password is enough. The guesser walks in as Ms. Rivera. Turn on the second proof and try again.";
      v.className = "verdict bad";
    }
  });
})();
