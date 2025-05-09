import React, { useState } from 'react';
import { Note, Recommendation } from '@/services/spaceService';
import { createNote, updateNote, deleteNote } from '@/services/spaceService';

interface NotesSectionProps {
  recommendation: Recommendation;
}

const NotesSection: React.FC<NotesSectionProps> = ({ recommendation }) => {
  const [notes, setNotes] = useState<Note[]>(recommendation.notes || []);
  const [newNote, setNewNote] = useState('');
  const [editingNoteId, setEditingNoteId] = useState<number | null>(null);
  const [editingContent, setEditingContent] = useState('');

  const handleAddNote = async () => {
    if (!newNote.trim()) return;
    
    try {
      const createdNote = await createNote({
        content: newNote,
        saved_recommendation_id: recommendation.id
      });
      
      setNotes([...notes, createdNote]);
      setNewNote('');
    } catch (error) {
      console.error('Error creating note:', error);
    }
  };

  const handleEditNote = async (noteId: number) => {
    if (!editingContent.trim()) return;
    
    try {
      const updatedNote = await updateNote(noteId, {
        content: editingContent
      });
      
      setNotes(notes.map(note => 
        note.id === noteId ? updatedNote : note
      ));
      
      setEditingNoteId(null);
      setEditingContent('');
    } catch (error) {
      console.error('Error updating note:', error);
    }
  };

  const handleDeleteNote = async (noteId: number) => {
    try {
      await deleteNote(noteId);
      setNotes(notes.filter(note => note.id !== noteId));
    } catch (error) {
      console.error('Error deleting note:', error);
    }
  };

  return (
    <div className="mt-8">
      <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-gray-100">Notes</h3>
      
      {/* Add new note */}
      <div className="mb-6">
        <textarea
          value={newNote}
          onChange={(e) => setNewNote(e.target.value)}
          placeholder="Add a new note..."
          className="w-full p-3 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-gray-100"
          rows={3}
        />
        <button
          onClick={handleAddNote}
          className="mt-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
        >
          Add Note
        </button>
      </div>
      
      {/* Notes list */}
      <div className="space-y-4">
        {notes.map((note) => (
          <div key={note.id} className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
            {editingNoteId === note.id ? (
              <div>
                <textarea
                  value={editingContent}
                  onChange={(e) => setEditingContent(e.target.value)}
                  className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-600 dark:text-gray-100"
                  rows={3}
                />
                <div className="mt-2 flex space-x-2">
                  <button
                    onClick={() => handleEditNote(note.id)}
                    className="px-3 py-1 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
                  >
                    Save
                  </button>
                  <button
                    onClick={() => {
                      setEditingNoteId(null);
                      setEditingContent('');
                    }}
                    className="px-3 py-1 bg-gray-200 dark:bg-gray-600 text-gray-700 dark:text-gray-200 rounded-md hover:bg-gray-300 dark:hover:bg-gray-500 transition-colors"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            ) : (
              <div>
                <p className="text-gray-700 dark:text-gray-200">{note.content}</p>
                <div className="mt-2 flex justify-between items-center">
                  <span className="text-sm text-gray-500 dark:text-gray-400">
                    {new Date(note.created_at).toLocaleDateString()}
                  </span>
                  <div className="flex space-x-2">
                    <button
                      onClick={() => {
                        setEditingNoteId(note.id);
                        setEditingContent(note.content);
                      }}
                      className="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300"
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => handleDeleteNote(note.id)}
                      className="text-red-600 dark:text-red-400 hover:text-red-800 dark:hover:text-red-300"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default NotesSection; 