"use strict";

// JavaScript lexical closure: the nested function retains the count binding.
function makeCounter(start = 0) {
    let count = start;

    return function increment() {
        count += 1;
        return count;
    };
}

const first = makeCounter(10);
const second = makeCounter(0);
console.log("first:", first(), first());
console.log("second:", second());
console.log("first again:", first());

// var creates ONE function-scoped binding shared by all closures.
const late = [];
for (var i = 0; i < 3; i++) {
    late.push(() => i * 3);
}

// let in a for loop gives each iteration a distinct captured binding.
const snapshots = [];
for (let j = 0; j < 3; j++) {
    snapshots.push(() => j * 3);
}
console.log("var loop:", late.map(fn => fn()));
console.log("let loop:", snapshots.map(fn => fn()));
