# SQL Query Outputs

All queries below are defined in `queries.py` and were run against the committed
`books.db` (474 books across 9 categories) via `python -m data_pipeline.queries`.
Output shown is real, unedited command output.

Clause coverage across the 5 queries: `SELECT`/`WHERE`, `ORDER BY`, `LIMIT`,
`DISTINCT`, `BETWEEN`, `IN`, and `JOIN` (used in two of the queries).

---

## 1. Cheapest in-stock books (WHERE, ORDER BY, LIMIT)

```sql
SELECT title, price_gbp
FROM books
WHERE in_stock = 1
ORDER BY price_gbp ASC
LIMIT 5;
```

Output:

```
('An Abundance of Katherines', 10.0)
('Patience', 10.16)
('I Am Pilgrim (Pilgrim #1)', 10.6)
('Counting Thyme', 10.62)
('The Complete Maus (Maus #1-2)', 10.64)
```

---

## 2. Distinct star ratings present (DISTINCT)

```sql
SELECT DISTINCT rating
FROM books
ORDER BY rating;
```

Output:

```
(1,)
(2,)
(3,)
(4,)
(5,)
```

---

## 3. Books priced £20-£30 (BETWEEN)

```sql
SELECT title, price_gbp
FROM books
WHERE price_gbp BETWEEN 20 AND 30
ORDER BY price_gbp ASC;
```

Output (100 rows):

```
('Blood Defense (Samantha Brinkman #1)', 20.3)
('Love, Lies and Spies', 20.55)
('Between Shades of Gray', 20.79)
('Delivering the Truth (Quaker Midwife Mystery #1)', 20.89)
('Sit, Stay, Love', 20.9)
('Fruits Basket, Vol. 6 (Fruits Basket #6)', 20.96)
('Tuesday Nights in 1980', 21.04)
('Voyager (Outlander #3)', 21.07)
('Boy Meets Boy', 21.12)
('Snatched: How A Drug Queen Went Undercover for the DEA and Was Kidnapped By Colombian Guerillas', 21.21)
('Saga, Volume 3 (Saga (Collected Editions) #3)', 21.57)
('Paper Girls, Vol. 1 (Paper Girls #1-5)', 21.71)
('Shadow Rites (Jane Yellowrock #10)', 21.72)
('Blink: The Power of Thinking Without Thinking', 21.74)
('Rising Strong', 21.82)
('No Dream Is Too High: Life Lessons From a Man Who Walked on the Moon', 21.95)
('Hystopia: A Novel', 21.96)
('Fifty Shades Darker (Fifty Shades #2)', 21.96)
('In the Country We Love: My Family Divided', 22.0)
('Ash', 22.06)
('Twenty Yawns', 22.08)
('The Art of Fielding', 22.1)
('Big Little Lies', 22.11)
('Giant Days, Vol. 2 (Giant Days #5-8)', 22.11)
('Letter to a Christian Nation', 22.2)
('Maybe Something Beautiful: How Art Transformed a Neighborhood', 22.54)
('The Requiem Red', 22.65)
('Charlie and the Chocolate Factory (Charlie Bucket #1)', 22.85)
('The Da Vinci Code (Robert Langdon #2)', 22.96)
('The Silkworm (Cormoran Strike #2)', 23.05)
('#HigherSelfie: Wake Up Your Life. Free Your Soul. Find Your Tribe.', 23.11)
('Three-Martini Lunch', 23.21)
('Rain Fish', 23.57)
('Lola and the Boy Next Door (Anna and the French Kiss #2)', 23.63)
('The Wedding Dress', 24.12)
('Harry Potter and the Prisoner of Azkaban (Harry Potter #3)', 24.17)
('My Mrs. Brown', 24.48)
('10% Happier: How I Tamed the Voice in My Head, Reduced Stress Without Losing My Edge, and Found Self-Help That Actually Works', 24.57)
('Career of Evil (Cormoran Strike #3)', 24.72)
('Soldier (Talon #3)', 24.72)
('The Little Paris Bookshop', 24.73)
('The Mysterious Affair at Styles (Hercule Poirot #1)', 24.8)
('Cometh the Hour (The Clifton Chronicles #6)', 25.01)
('Saga, Volume 6 (Saga (Collected Editions) #6)', 25.02)
("Love That Boy: What Two Presidents, Eight Road Trips, and My Son Taught Me About a Parent's Expectations", 25.06)
('Nap-a-Roo', 25.08)
("Talking to Girls About Duran Duran: One Young Man's Quest for True Love and a Cooler Haircut", 25.15)
('Chase Me (Paris Nights #2)', 25.27)
('What Happened on Beale Street (Secrets of the South Mysteries #2)', 25.37)
('Through the Woods', 25.38)
('Extreme Prey (Lucas Davenport #26)', 25.4)
('Red Hood/Arsenal, Vol. 1: Open for Business (Red Hood/Arsenal #1)', 25.48)
('Starlark', 25.83)
('The First Hostage (J.B. Collins #2)', 25.85)
('Cinder (The Lunar Chronicles #1)', 26.09)
('The Nightingale', 26.26)
('The Day the Crayons Came Home (Crayons)', 26.33)
('Still Life with Bread Crumbs', 26.41)
('Reasons to Stay Alive', 26.41)
('Atlas Shrugged', 26.58)
('Gratitude', 26.66)
('Girl With a Pearl Earring', 26.77)
('Let It Out: A Journey Through Journaling', 26.79)
('Poisonous (Max Revere Novels #3)', 26.8)
('13 Hours: The Inside Account of What Really Happened In Benghazi', 27.06)
('Eligible (The Austen Project #4)', 27.09)
('This Is Where It Ends', 27.12)
('The Widow', 27.26)
('Born to Run: A Hidden Tribe, Superathletes, and the Greatest Race the World Has Never Seen', 27.35)
('The Infinities', 27.41)
("Best of My Love (Fool's Gold #20)", 27.41)
('Becoming Wise: An Inquiry into the Mystery and Art of Living', 27.43)
('Lost Among the Living', 27.7)
('God Is Not Great: How Religion Poisons Everything', 27.8)
('The Time Keeper', 27.88)
('The Demon Prince of Momochi House, Vol. 4 (The Demon Prince of Momochi House #4)', 27.88)
('The Haters', 27.89)
('The Shack', 28.03)
('The Marriage of Opposites', 28.08)
('Avatar: The Last Airbender: Smoke and Shadow, Part 3 (Smoke and Shadow #3)', 28.09)
('A Fierce and Subtle Poison', 28.13)
("The Geography of Bliss: One Grump's Search for the Happiest Places in the World", 28.23)
('The Passion of Dolssa', 28.32)
('Rhythm, Chord & Malykhin', 28.34)
('Matilda', 28.34)
("The Midnight Assassin: Panic, Scandal, and the Hunt for America's First Serial Killer", 28.45)
('Saga, Volume 1 (Saga (Collected Editions) #1)', 28.48)
('Red: The True Story of Red Riding Hood', 28.54)
('Burning', 28.81)
('Hold Your Breath (Search and Rescue #1)', 28.82)
("In the Garden of Beasts: Love, Terror, and an American Family in Hitler's Berlin", 28.85)
('I Am Malala: The Girl Who Stood Up for Education and Was Shot by the Taliban', 28.88)
('Mr. Mercedes (Bill Hodges Trilogy #1)', 28.9)
('South of Sunshine', 28.93)
('Origins (Alphas 0.5)', 28.99)
('Call the Nurse: True Stories of a Country Nurse on a Scottish Isle', 29.14)
('Looking for Lovely: Collecting the Moments that Matter', 29.14)
('I Hate Fairyland, Vol. 1: Madly Ever After (I Hate Fairyland (Compilations) #1-5)', 29.17)
('The Mirror & the Maze (The Wrath and the Dawn #1.5)', 29.38)
("Man's Search for Meaning", 29.48)
('The Land of 10,000 Madonnas', 29.64)
('Island of Dragons (Unwanteds #7)', 29.65)
('Forever and Forever: The Courtship of Henry Longfellow and Fanny Appleton', 29.69)
('Ouran High School Host Club, Vol. 1 (Ouran High School Host Club #1)', 29.87)
('Frostbite (Vampire Academy #2)', 29.99)
('Under the Banner of Heaven: A Story of Violent Faith', 30.0)
```

---

## 4. Books in selected categories (IN, JOIN)

```sql
SELECT b.title, c.category_name
FROM books b
JOIN categories c ON b.category_id = c.category_id
WHERE c.category_name IN ('Fiction', 'Mystery', 'Fantasy')
ORDER BY c.category_name, b.title
LIMIT 10;
```

Output:

```
('A Court of Thorns and Roses (A Court of Thorns and Roses #1)', 'Fantasy')
('A Feast for Crows (A Song of Ice and Fire #4)', 'Fantasy')
('A Gathering of Shadows (Shades of Magic #2)', 'Fantasy')
('A Shard of Ice (The Black Symphony Saga #1)', 'Fantasy')
('A Storm of Swords (A Song of Ice and Fire #3)', 'Fantasy')
('Ash', 'Fantasy')
('Avatar: The Last Airbender: Smoke and Shadow, Part 3 (Smoke and Shadow #3)', 'Fantasy')
('City of Glass (The Mortal Instruments #3)', 'Fantasy')
('Crown of Midnight (Throne of Glass #2)', 'Fantasy')
('Darkfever (Fever #1)', 'Fantasy')
```

---

## 5. Average price per category (JOIN, aggregation)

```sql
SELECT c.category_name, COUNT(*) AS book_count, ROUND(AVG(b.price_gbp), 2) AS avg_price_gbp
FROM books b
JOIN categories c ON b.category_id = c.category_id
GROUP BY c.category_name
ORDER BY avg_price_gbp DESC;
```

Output:

```
('Fantasy', 48, 39.59)
('Fiction', 65, 36.07)
('Young Adult', 54, 35.45)
('Sequential Art', 75, 34.57)
('Nonfiction', 110, 34.26)
('Romance', 35, 33.93)
('Historical Fiction', 26, 33.64)
('Childrens', 29, 32.64)
('Mystery', 32, 31.72)
```
