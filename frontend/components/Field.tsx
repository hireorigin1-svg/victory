type FieldProps = {
  label: string;
  name: string;
  value: string;
  onChange: (name: string, value: string) => void;
  textarea?: boolean;
  type?: string;
};

export function Field({
  label,
  name,
  value,
  onChange,
  textarea = false,
  type = "text"
}: FieldProps) {
  const shared =
    "w-full rounded border border-line bg-white px-3 py-2 text-sm outline-none transition focus:border-signal focus:ring-2 focus:ring-signal/20";

  return (
    <label className="grid gap-1 text-sm font-medium text-ink">
      <span>{label}</span>
      {textarea ? (
        <textarea
          className={`${shared} min-h-20 resize-y`}
          name={name}
          value={value}
          onChange={(event) => onChange(name, event.target.value)}
        />
      ) : (
        <input
          className={shared}
          name={name}
          type={type}
          value={value}
          onChange={(event) => onChange(name, event.target.value)}
        />
      )}
    </label>
  );
}
