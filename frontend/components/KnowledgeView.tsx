'use client';

import { useState, useEffect, useRef } from 'react';

interface Document {
  id: string;
  name: string;
  path: string;
  size: number;
  modified: number;
  type: string;
  indexed: boolean;
  chunks: number;
}

export default function KnowledgeView() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [reindexing, setReindexing] = useState(false);
  const [selectedDocs, setSelectedDocs] = useState<Set<string>>(new Set());
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    try {
      setLoading(true);
      const apiHost = process.env.NEXT_PUBLIC_API_HOST || 'http://localhost:8000';
      const response = await fetch(`${apiHost}/documents`);
      const data = await response.json();
      
      if (data.success) {
        setDocuments(data.documents);
      } else {
        setError('Failed to load documents');
      }
    } catch (err) {
      setError('Error connecting to server');
    } finally {
      setLoading(false);
    }
  };

  const handleUpload = async (files: FileList) => {
    if (files.length === 0) return;

    setUploading(true);
    setError(null);

    const formData = new FormData();
    Array.from(files).forEach(file => {
      formData.append('files', file);
    });

    try {
      const apiHost = process.env.NEXT_PUBLIC_API_HOST || 'http://localhost:8000';
      const response = await fetch(`${apiHost}/index/upload`, {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();
      
      if (data.success) {
        await loadDocuments();
      } else {
        setError(data.error || 'Upload failed');
      }
    } catch (err) {
      setError('Error uploading files');
    } finally {
      setUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleDelete = async (docId: string) => {
    if (!confirm('Are you sure you want to delete this document?')) return;

    try {
      const apiHost = process.env.NEXT_PUBLIC_API_HOST || 'http://localhost:8000';
      const response = await fetch(`${apiHost}/documents/${encodeURIComponent(docId)}`, {
        method: 'DELETE',
      });

      const data = await response.json();
      
      if (data.success) {
        await loadDocuments();
        // No need to show reindex message as it's handled automatically
      } else {
        setError(data.error || 'Delete failed');
      }
    } catch (err) {
      setError('Error deleting document');
    }
  };

  const handleReindex = async () => {
    setReindexing(true);
    setError(null);

    try {
      const apiHost = process.env.NEXT_PUBLIC_API_HOST || 'http://localhost:8000';
      const response = await fetch(`${apiHost}/documents/reindex`, {
        method: 'POST',
      });

      const data = await response.json();
      
      if (data.success) {
        setError(null);
        alert(`Successfully reindexed ${data.documents_indexed} documents`);
      } else {
        setError(data.error || 'Reindex failed');
      }
    } catch (err) {
      setError('Error reindexing documents');
    } finally {
      setReindexing(false);
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (timestamp: number) => {
    return new Date(timestamp * 1000).toLocaleDateString();
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Knowledge Documents</h2>
            <p className="text-gray-600 mt-1">Manage your document library for AI-powered search and retrieval</p>
          </div>
          <div className="flex gap-3">
            <button
              onClick={() => fileInputRef.current?.click()}
              disabled={uploading}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
            >
              {uploading ? 'Uploading...' : 'Upload Documents'}
            </button>
            <button
              onClick={handleReindex}
              disabled={reindexing || documents.length === 0}
              className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50"
            >
              {reindexing ? 'Reindexing...' : 'Reindex All'}
            </button>
          </div>
        </div>

        {/* Hidden file input */}
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept=".pdf,.txt,.docx"
          onChange={(e) => e.target.files && handleUpload(e.target.files)}
          className="hidden"
        />

        {/* Error message */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
            {error}
          </div>
        )}
      </div>

      {/* Document list */}
      <div className="bg-white rounded-lg border border-gray-200">
        {loading ? (
          <div className="p-8 text-center text-gray-500">
            Loading documents...
          </div>
        ) : documents.length === 0 ? (
          <div className="p-8 text-center">
            <div className="text-gray-500 mb-4">No documents uploaded yet</div>
            <button
              onClick={() => fileInputRef.current?.click()}
              className="text-blue-600 hover:text-blue-700"
            >
              Upload your first document
            </button>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left px-6 py-3 text-sm font-medium text-gray-700">Name</th>
                  <th className="text-left px-6 py-3 text-sm font-medium text-gray-700">Type</th>
                  <th className="text-left px-6 py-3 text-sm font-medium text-gray-700">Size</th>
                  <th className="text-left px-6 py-3 text-sm font-medium text-gray-700">Modified</th>
                  <th className="text-left px-6 py-3 text-sm font-medium text-gray-700">Status</th>
                  <th className="text-right px-6 py-3 text-sm font-medium text-gray-700">Actions</th>
                </tr>
              </thead>
              <tbody>
                {documents.map((doc) => (
                  <tr key={doc.id} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="px-6 py-4">
                      <div className="flex items-center">
                        <span className="text-2xl mr-3">
                          {doc.type === 'pdf' ? '📄' : doc.type === 'txt' ? '📝' : '📋'}
                        </span>
                        <span className="text-gray-900">{doc.name}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-gray-600 uppercase text-sm">{doc.type}</td>
                    <td className="px-6 py-4 text-gray-600">{formatFileSize(doc.size)}</td>
                    <td className="px-6 py-4 text-gray-600">{formatDate(doc.modified)}</td>
                    <td className="px-6 py-4">
                      {doc.indexed ? (
                        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                          Indexed ({doc.chunks} chunks)
                        </span>
                      ) : (
                        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                          Not indexed
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4 text-right">
                      <button
                        onClick={() => handleDelete(doc.id)}
                        className="text-red-600 hover:text-red-700 text-sm font-medium"
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Stats */}
      {documents.length > 0 && (
        <div className="mt-6 flex gap-6 text-sm text-gray-600">
          <div>
            <span className="font-medium">{documents.length}</span> documents
          </div>
          <div>
            <span className="font-medium">
              {formatFileSize(documents.reduce((sum, doc) => sum + doc.size, 0))}
            </span> total
          </div>
        </div>
      )}
    </div>
  );
}