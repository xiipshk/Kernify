// Задача: Удаление пробелов
// Тема: Строки и текст
// Сложность: easy
// Описание: strip, replace
// Источник: ОГЭ/ЕГЭ информатика, Codeforces, acmp.ru, informatics.msk.ru

package main

import (
	"bufio"
	"fmt"
	"os"
	"strconv"
)

var (
	scanner = bufio.NewScanner(os.Stdin)
	writer  = bufio.NewWriter(os.Stdout)
)

func init() {
	scanner.Split(bufio.ScanWords)
}

func next() string {
	scanner.Scan()
	return scanner.Text()
}

func nextInt() int {
	x, _ := strconv.Atoi(next())
	return x
}

func printf(f string, a ...interface{}) {
	fmt.Fprintf(writer, f, a...)
}

func println(a ...interface{}) {
	fmt.Fprintln(writer, a...)
}

func solve() {
    // TODO: Реализовать решение
    pass

writer.Flush()
}
