let attempts, strike, out, ball;
let first, second, third;
let success, fail;
let i1, i2, i3, v1, v2, v3;

function reset() {
    attempts = 9;
    success = false;
    fail = false;
    document.querySelector(".submit-button").disabled = false;

    // 중복 없는 랜덤 숫자 생성
    const digits = [];
    while (digits.length < 3) {
    const n = Math.floor(Math.random() * 10);
    if (!digits.includes(n)) digits.push(n);
    }
    [first, second, third] = digits;
    
    // 화면 초기화
    updateAttempts();
    document.getElementById("results").innerHTML = "";
    document.getElementById("game-result-img").src = "";
}

function readInput() {
    v1 = document.getElementById("number1").value.trim();
    v2 = document.getElementById("number2").value.trim();
    v3 = document.getElementById("number3").value.trim();
    
    i1 = parseInt(v1);
    i2 = parseInt(v2);
    i3 = parseInt(v3);

    return { i1, i2, i3, v1, v2, v3 };
}

function updateAttempts() {
    const attemptsText = document.getElementById("attempts");
    if (attemptsText) attemptsText.textContent = String(attempts);
}

function printResult() {
    const gameResultImg = document.getElementById("game-result-img");
    const results = document.getElementById("results");

    // 한 줄 만들기
    const row = document.createElement("div");
    row.style.display = "flex";
    row.style.alignItems = "center";
    row.style.justifyContent = "space-between";
    row.style.gap = "100px";
    row.style.margin = "10px 0";

    // 왼쪽: 입력 숫자들
    const left = document.createElement("div");
    left.classList.add("left");
    left.textContent = `${i1} ${i2} ${i3}`;

    // 오른쪽: 결과 표시
    const right = document.createElement("div");
    right.classList.add("right");
    right.style.display = "flex";
    right.style.alignItems = "center";
    right.style.gap = "8px";

    if (out) {
        const o = document.createElement("span");
        o.classList.add("out", "num-result");
        o.textContent = "O";
        right.appendChild(o);
    } 
    else {
        // 숫자 strike
        const sNum = document.createElement("span");
        sNum.textContent = String(strike);

        // S
        const sCircle = document.createElement("span");
        sCircle.classList.add("strike", "num-result");
        sCircle.textContent = "S";

        // 숫자 ball
        const bNum = document.createElement("span");
        bNum.textContent = String(ball);

        // B
        const bCircle = document.createElement("span");
        bCircle.classList.add("ball", "num-result");
        bCircle.textContent = "B";

        right.appendChild(sNum);
        right.appendChild(sCircle);
        right.appendChild(bNum);
        right.appendChild(bCircle);
    }

    // row에 합치기
    row.appendChild(left);
    row.append(" : ");
    row.appendChild(right);
    results.appendChild(row);

    if (success) gameResultImg.src = "./success.png";
    else if (fail) gameResultImg.src = "./fail.png";
}

function check_numbers() {
    readInput();

    document.getElementById("number1").value = "";
    document.getElementById("number2").value = "";
    document.getElementById("number3").value = "";

    if(v1 === "" || v2 === "" || v3 === "") return;

    attempts--;

    strike = 0;
    ball = 0;
    out = 0;

    // 계산
    if (i1 === first) strike++;
    else if (i1 === second || i1 === third) ball++;

    if (i2 === second) strike++;
    else if (i2 === first || i2 === third) ball++;

    if (i3 === third) strike++;
    else if (i3 === first || i3 === second) ball++;

    if (strike === 0 && ball === 0) out = 1;

    // 성공
    if (strike === 3) success = true;

    // 실패
    if (!success && attempts === 0) fail = true;

    // 게임이 끝났을 시 버튼 비활성화
    if (success || fail) {
        const btn = document.querySelector(".submit-button");
        
        btn.disabled = true;
        btn.style.opacity = "0.5";
        btn.style.cursor = "not-allowed";
    }

    // 화면 업데이트
    updateAttempts();
    printResult();
}

// 처음 시작할 때 리셋
window.onload = function () {
    reset();
};
