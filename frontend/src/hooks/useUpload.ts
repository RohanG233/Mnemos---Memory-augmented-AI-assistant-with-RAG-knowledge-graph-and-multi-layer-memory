import {
  useEffect,
  useState
} from "react";

import {
  useAuth
} from "../context/AuthContext";

import {
  deleteDocument,
  getDocuments,
  uploadDocument
} from "../services/uploadService";

import type {
  UploadedDocument
} from "../types/upload";


export function useUpload() {

  const {
    accessToken
  } = useAuth();


  const [
    documents,
    setDocuments
  ] = useState<
    UploadedDocument[]
  >([]);


  const [
    loading,
    setLoading
  ] = useState(false);


  const [
    error,
    setError
  ] = useState<
    string | null
  >(null);


  const [
    success,
    setSuccess
  ] = useState<
    string | null
  >(null);


  // -----------------------------
  // Load existing documents
  // -----------------------------

  useEffect(() => {

    async function loadDocuments() {

      if (!accessToken) {
        return;
      }

      try {

        const response =
          await getDocuments(
            accessToken
          );

        setDocuments(
          response.documents
        );

      } catch (err) {

        setError(
          err instanceof Error
            ? err.message
            : "Failed to load documents."
        );

      }
    }


    loadDocuments();

  }, [
    accessToken
  ]);


  // -----------------------------
  // Upload document
  // -----------------------------

  async function upload(
    file: File
  ) {

    if (!accessToken) {

      setError(
        "You are not authenticated."
      );

      return;
    }


    setError(null);
    setSuccess(null);
    setLoading(true);


    try {

      const response =
        await uploadDocument(
          file,
          accessToken
        );


      const document: UploadedDocument = {
        document_id:
          response.document_id,

        filename:
          response.filename,

        chunks:
          response.chunks,
      };


      setDocuments(
        (
          previousDocuments
        ) => [

          ...previousDocuments,

          document
        ]
      );


      setSuccess(
        response.message
      );

    } catch (err) {

      setError(
        err instanceof Error
          ? err.message
          : "Upload failed."
      );

    } finally {

      setLoading(false);

    }
  }


  // -----------------------------
  // Delete document
  // -----------------------------

  async function removeDocument(
    documentId: string
  ) {

    if (!accessToken) {

      setError(
        "You are not authenticated."
      );

      return;
    }


    setError(null);
    setSuccess(null);
    setLoading(true);


    try {

      await deleteDocument(
        documentId,
        accessToken
      );


      setDocuments(
        (
          previousDocuments
        ) =>
          previousDocuments.filter(
            (document) =>
              document.document_id !==
              documentId
          )
      );


      setSuccess(
        "Document removed successfully."
      );

    } catch (err) {

      setError(
        err instanceof Error
          ? err.message
          : "Failed to remove document."
      );

    } finally {

      setLoading(false);

    }
  }


  return {

    documents,

    upload,

    removeDocument,

    loading,

    error,

    success,
  };
}