from django.test import TestCase
from django.urls import reverse
from datetime import date

from .models import Todo


class TodoModelTests(TestCase):
    def test_create_todo_with_minimal_fields(self):
        todo = Todo.objects.create(title="Buy milk")
        self.assertEqual(todo.title, "Buy milk")
        self.assertFalse(todo.is_resolved)
        self.assertIsNone(todo.due_date)

    def test_todo_str_representation(self):
        todo = Todo.objects.create(title="Buy milk", is_resolved=False)
        text = str(todo)
        self.assertIn("Buy milk", text)
        # We defined __str__ to include 'Open'/'Done'
        self.assertTrue("Open" in text or "Done" in text)


class TodoViewTests(TestCase):
    def setUp(self):
        self.todo_open = Todo.objects.create(
            title="Open task",
            description="Do something",
            due_date=date.today(),
            is_resolved=False,
        )
        self.todo_done = Todo.objects.create(
            title="Done task",
            description="Already done",
            due_date=date.today(),
            is_resolved=True,
        )

    def test_todo_list_view_displays_todos(self):
        url = reverse("todo_list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "todo/todo_list.html")

        todos_in_context = response.context["todos"]
        self.assertEqual(todos_in_context.count(), 2)
        self.assertIn(self.todo_open, todos_in_context)
        self.assertIn(self.todo_done, todos_in_context)

    def test_todo_create_view_get(self):
        url = reverse("todo_create")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "todo/todo_form.html")
        self.assertIn("form", response.context)

    def test_todo_create_view_post_valid_data(self):
        url = reverse("todo_create")
        payload = {
            "title": "New task",
            "description": "Details here",
            "due_date": "2030-01-01",
            # omit is_resolved -> should default to False in model
        }
        response = self.client.post(url, data=payload)

        # should redirect back to list
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("todo_list"))

        # object should exist in DB
        todo = Todo.objects.get(title="New task")
        self.assertEqual(todo.description, "Details here")
        self.assertEqual(str(todo.due_date), "2030-01-01")
        self.assertFalse(todo.is_resolved)

    def test_todo_update_view_get(self):
        url = reverse("todo_update", args=[self.todo_open.pk])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "todo/todo_form.html")
        self.assertIn("form", response.context)
        self.assertEqual(response.context["form"].instance, self.todo_open)

    def test_todo_update_view_post_valid_data(self):
        url = reverse("todo_update", args=[self.todo_open.pk])
        payload = {
            "title": "Updated title",
            "description": "Updated description",
            "due_date": "2035-12-31",
            "is_resolved": True,
        }
        response = self.client.post(url, data=payload)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("todo_list"))

        self.todo_open.refresh_from_db()
        self.assertEqual(self.todo_open.title, "Updated title")
        self.assertTrue(self.todo_open.is_resolved)
        self.assertEqual(str(self.todo_open.due_date), "2035-12-31")

    def test_todo_delete_view_get(self):
        url = reverse("todo_delete", args=[self.todo_open.pk])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "todo/todo_confirm_delete.html")
        self.assertEqual(response.context["todo"], self.todo_open)

    def test_todo_delete_view_post_deletes_object(self):
        url = reverse("todo_delete", args=[self.todo_open.pk])
        response = self.client.post(url)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("todo_list"))
        self.assertFalse(Todo.objects.filter(pk=self.todo_open.pk).exists())

    def test_toggle_resolved_view_marks_done(self):
        # start as open
        self.assertFalse(self.todo_open.is_resolved)

        url = reverse("todo_toggle_resolved", args=[self.todo_open.pk])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("todo_list"))

        self.todo_open.refresh_from_db()
        self.assertTrue(self.todo_open.is_resolved)

    def test_toggle_resolved_view_marks_open_again(self):
        # start as done
        self.assertTrue(self.todo_done.is_resolved)

        url = reverse("todo_toggle_resolved", args=[self.todo_done.pk])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("todo_list"))

        self.todo_done.refresh_from_db()
        self.assertFalse(self.todo_done.is_resolved)
