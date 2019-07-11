int main()
{
  int a = 1, b = 2, c = 3, d = 0;
  while (c != 5 && a < 4 || b == 1)
  {
    if (a >= c + d || b - d < a && c != d)
      a = a + 1;
    c = c - 1;
  }
}
