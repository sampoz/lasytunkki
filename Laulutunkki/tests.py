from django.test import TestCase
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

from Laulutunkki.models import *
from Laulutunkki.booklet import *

# Create your tests here.

class UserProfileTestCase(TestCase):
	def setUp(self):
		self.u1 = User.objects.create(username='user1')
		self.u1.save()

	def test_create_user_profile(self):
		create_user_profile(sender=self.u1, instance=self.u1, created=False)
		up1 = UserProfile.objects.get(user=self.u1)
		self.assertNotEqual(up1, None, 'The userprofile was not created successfully.')


class SongTestCase(TestCase):
  def setUp(self):
		self.u1 = User.objects.create(username='user1', email="user1@email.com")
		self.u1.save()

		self.u2 = User.objects.create(username='user2', email="user2@email.com")
		self.u2.save()

		self.s1 = Song.objects.create(title="Test Song 1",
			category="Test category 1",
			lyrics="Laa laa laa 1",
			author=self.u1)
		self.s1.save()

		self.s2 = Song.objects.create(title="Test Song 2",
			category="Test category 1",
			lyrics="Laa laa laa 1",
			author=self.u2)
		self.s2.save()


  def test_create_song(self):
    self.assertNotEqual(self.s1, None, 'The song was not created successfully.')
    self.s1 = Song.objects.create(title="Test Song 15",
      category="Test category 1",
      lyrics="Laa laa laa 1",
      author=self.u1)
    self.assertEqual(get_object_or_404(Song, pk=3), self.s1, 'The song was not created successfully.')

  def test_song_modify(self):
    instance = get_object_or_404(Song, pk=1)
    instance.title = "Modified title 1"
    instance.save()
    self.assertEqual(get_object_or_404(Song, pk=1).title, "Modified title 1", 'The song was not modified successfully.')

  def test_song_like(self):
    self.sl1 = SongLike.objects.create(user=self.u1, song=self.s1, value=True)
    self.assertTrue(self.sl1.value, 'The like was not positive')

    self.sl2 = SongLike.objects.create(user=self.u1, song=self.s1, value=False)
    self.assertFalse(self.sl2.value, 'The like was not negative')


class BookletOptimizationTestCase(TestCase):
  def setUp(self):
    self.user = User.objects.create(username='user1')
    self.user.save()
    self.song1 = Song.objects.create(title="Test Song 1",
      category="Test category 1",
      lyrics="Laa laa laa 1",
      author=self.user)
    self.song2 = Song.objects.create(title="Test Song 2",
      category="Test category 2",
      lyrics="Laa laa laa 2 \r\n next line",
      author=self.user)
    self.song1.save()
    self.song2.save()
    long_lyrics = ""
    for x in xrange(1,10):
      long_lyrics += "a \r\n"
    self.song3 = Song.objects.create(title="Test Song 3",
      category="Test category 3",
      lyrics=long_lyrics,
      author=self.user)
    self.song3.save()


  def test_single_song_row_count(self):
    self.assertEqual(count_rows_for_song(self.song1), 4, 
      "Song should contain one line plus three lines for header")
    self.assertEqual(count_rows_for_song(self.song2), 5, 
      "Song should contain two line plus three lines for header")
    self.assertEqual(count_rows_for_song(None), 0, "If no song given result should be 0")

  def test_multiple_songs_row_count(self):
    songs = [self.song1, self.song2]
    songs_len = count_rows_for_songs(songs)
    self.assertEqual(len(songs_len), 2, 
      "Dict should contain two object")
    self.assertEqual(songs_len[self.song1.id], 4,
      "Line count should match to four")
    self.assertEqual(songs_len[self.song2.id], 5,
      "Line count should match to five")
    self.assertEqual(len(count_rows_for_songs(None)), 0, 
      "If no songs given dict len should be 0")
    self.assertEqual(len(count_rows_for_songs([])), 0, 
      "If empty list given dict len should be 0")

  def test_page_optimization(self):
    song_len = count_rows_for_songs([self.song3])
    pages1 = pages_optimization_simple(song_len, 10, [self.song3.id])
    self.assertEqual(len(pages1), 1, "One should fit in one page")
    self.assertEqual(len(pages1[0]), 1, "Page should contain one song")
    self.assertEqual(pages1[0][0], self.song3.id, "Song ids should match")

    songs_len = count_rows_for_songs([self.song1, self.song2])
    pages2 = pages_optimization_simple(songs_len, 10, [self.song1.id, self.song2.id])
    self.assertEqual(len(pages2[0]), 2, "Page should contain two song")
    self.assertEqual(pages2[0][0], self.song1.id, "Song ids should match")
    self.assertEqual(pages2[0][1], self.song2.id, "Song ids should match")
    self.assertEqual(len(pages2), 1, "These two song should fit in one page")

    songs_len2 = count_rows_for_songs([self.song1, self.song2, self.song3])
    pages3 = pages_optimization_simple(songs_len2, 10, 
      [self.song1.id, self.song2.id, self.song3.id])
    self.assertEqual(len(pages3), 2, "Result should be two pages")
    self.assertEqual(len(pages3[0]), 2, "Page should contain two song")
    self.assertEqual(pages3[1][0], self.song3.id, "Song id should match")

    zero_page = pages_optimization_simple({}, 10 , [])
    self.assertEqual(len(zero_page), 1, "If no songs given result should be empty page")

  def test_sort_songs_for_pages(self):
    result = sort_songs_for_pages(Song.objects.all(),
      10, [self.song1.id, self.song2.id, self.song3.id])
    self.assertEqual(len(result), 2, "Result should be two pages")
    self.assertEqual(len(result[0]), 2, "Page should contain two song")
    self.assertEqual(result[1][0], self.song3.id, "Song id should match")
    with self.assertRaises(ValueError):
      sort_songs_for_pages(Song.objects.filter(id=self.song1.id), 10,
      [self.song1.id, self.song2.id])

  def test_optimization_result_to_song_object_lists(self):
    songs = Song.objects.all()
    opt = sort_songs_for_pages(songs,
      10, [self.song1.id, self.song2.id, self.song3.id])
    converted = optimization_result_to_song_object_lists(songs, 
      opt)
    self.assertEqual(len(converted), len(opt), 
      "Song id list len and song object list len should be equal")
    self.assertEqual(converted[1][0], self.song3, 
      "Second page first song should still be song3")

  def test_convert_song_ids_to_song_object_list(self):
    songs = Song.objects.all()
    song_ids = [self.song1.id, self.song2.id, self.song3.id]
    object_list = convert_song_ids_to_song_object_list(songs, song_ids)
    self.assertEqual(object_list[0].id, song_ids[0], 
      "Position for first object should be same")
    self.assertEqual(object_list[1].id, song_ids[1], 
      "Position for second object should be same")
    self.assertEqual(object_list[2].id, song_ids[2], 
      "Position for third object should be same")

    

class BookletCreationTestCase(TestCase):
  def setUp(self):
    self.user = User.objects.create(username='user1')
    self.user.save()
    self.song1 = Song.objects.create(title="Test Song 1",
      category="Test category 1",
      lyrics="Laa laa laa 1",
      author=self.user)
    self.song2 = Song.objects.create(title="Test Song 2",
      category="Test category 2",
      lyrics="Laa laa laa 2 \r\n next line",
      author=self.user)
    self.song1.save()
    self.song2.save()
    long_lyrics = ""
    for x in xrange(1,80):
      long_lyrics += "a \r\n"
    self.song3 = Song.objects.create(title="Test Song 3",
      category="Test category 3",
      lyrics=long_lyrics,
      author=self.user)
    self.song3.save()
    self.songs = Song.objects.all()
    self.song_ids = [self.song1.id, self.song2.id, self.song3.id]
    self.pages = create_pages_song_lists(self.songs, self.song_ids)

  def test_create_booklet_pages(self):
    booklet = Booklet(title="title",
      author=self.user, 
      pdf_file=None,
      front_page_text="front_page_text", 
      front_page_image="")
    booklet.save()
    create_booklet_pages(booklet, self.pages)
    self.assertEqual(len(booklet.pages.all()), 2, "Booklet should have 2 page")
    page1 = booklet.pages.all()[0]
    self.assertTrue(page1.songs.filter(song=self.song1).exists(), 
      "First page should contain song1")
    page1 = booklet.pages.all()[1]
    self.assertTrue(page1.songs.filter(song=self.song3).exists(), 
      "second page should contain song3")

  def test_create_booklet(self):
    create_booklet(self.pages, self.user, "Test Booklet", "Test")
    self.assertEqual(len(Booklet.objects.all()), 1, 
      "There should be one booklet")
    booklet = Booklet.objects.all()[0]
    self.assertEqual(len(booklet.pages.all()), 2,
      "This booklet should have 2 pages")
    self.assertEqual(booklet.title, "Test Booklet", "Titles should match")
    self.assertEqual(booklet.author, self.user, "author should be same user")
    self.assertEqual(booklet.front_page_text, "Test", 
      "Front page test should be test")

  def test_update_booklet(self):
    booklet = create_booklet(self.pages, self.user, "Test Booklet", "Test")
    update_booklet(booklet, self.songs, "New Test Booklet", [self.song3.id], 
      "New Test")
    self.assertEqual(booklet.title, "New Test Booklet", 
      "Name should have been changed")
    self.assertEqual(booklet.front_page_text, "New Test", 
      "Name should have been changed")
    self.assertEqual(len(booklet.pages.all()), 1,
      "This booklet should have 1 page now")
