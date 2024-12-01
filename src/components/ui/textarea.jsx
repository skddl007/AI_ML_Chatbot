// src/components/ui/textarea.jsx

import React from 'react';

export function Textarea({ id, value, onChange, placeholder }) {
  return (
    <textarea
      id={id}
      value={value}
      onChange={onChange}
      placeholder={placeholder}
      className="textarea"
    />
  );
}
