// Задача: Разделение файла
// Тема: Работа с файлами
// Сложность: medium
// Описание: По N строк
// Источник: ОГЭ/ЕГЭ информатика, Codeforces, acmp.ru, informatics.msk.ru

const fs = require('fs');
const input = fs.readFileSync(0, 'utf-8').trim().split(/\s+/);
let idx = 0;
const next = () => input[idx++];
const nextInt = () => parseInt(next());

function solve() {
    // TODO: Реализовать решение
    pass

solve();
