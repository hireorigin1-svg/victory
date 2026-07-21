"use client";

import { useEffect, useMemo, useState } from "react";

type FieldProps = {
  label: string;
  name: string;
  value: string;
  onChange: (name: string, value: string) => void;
  textarea?: boolean;
  type?: string;
  options?: string[];
};

export function Field({
  label,
  name,
  value,
  onChange,
  textarea = false,
  type = "text",
  options = []
}: FieldProps) {
  const shared =
    "w-full rounded border border-line bg-white px-3 py-2 text-sm outline-none transition focus:border-signal focus:ring-2 focus:ring-signal/20";
  const customValue = "__custom__";
  const optionKey = useMemo(() => options.join("|"), [options]);
  const hasOptions = options.length > 0;
  const hasPresetValue = hasOptions && options.includes(value);
  const [customMode, setCustomMode] = useState(hasOptions && Boolean(value) && !hasPresetValue);

  useEffect(() => {
    if (!hasOptions) {
      setCustomMode(false);
      return;
    }
    if (value && !options.includes(value)) {
      setCustomMode(true);
    }
    if (value && options.includes(value)) {
      setCustomMode(false);
    }
  }, [hasOptions, optionKey, options, value]);

  const manualInput = textarea ? (
    <textarea
      className={`${shared} min-h-20 resize-y`}
      name={name}
      placeholder={hasOptions ? `Type custom ${label.toLowerCase()}` : undefined}
      value={value}
      onChange={(event) => onChange(name, event.target.value)}
    />
  ) : (
    <input
      className={shared}
      name={name}
      placeholder={hasOptions ? `Type custom ${label.toLowerCase()}` : undefined}
      type={type}
      value={value}
      onChange={(event) => onChange(name, event.target.value)}
    />
  );

  return (
    <label className="grid gap-1 text-sm font-medium text-ink">
      <span>{label}</span>
      {hasOptions ? (
        <select
          className="h-10 rounded border border-line bg-white px-3 text-sm outline-none transition focus:border-signal focus:ring-2 focus:ring-signal/20"
          name={`${name}_preset`}
          value={customMode ? customValue : value}
          onChange={(event) => {
            const nextValue = event.target.value;
            if (nextValue === customValue) {
              setCustomMode(true);
              if (hasPresetValue) {
                onChange(name, "");
              }
              return;
            }
            setCustomMode(false);
            onChange(name, nextValue);
          }}
        >
          <option value="">Select {label}</option>
          {options.map((option) => (
            <option key={option} value={option}>
              {option}
            </option>
          ))}
          <option value={customValue}>Other / custom</option>
        </select>
      ) : null}
      {hasOptions && customMode ? manualInput : null}
      {!hasOptions ? manualInput : null}
    </label>
  );
}
