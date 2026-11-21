// Задача: Подсчет строк/слов/символов
// Тема: Работа с файлами
// Сложность: easy
// Описание: wc аналог
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
