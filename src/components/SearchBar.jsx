import { useState } from "react";
import { Search } from "lucide-react";

export default function SearchBar({ onSearch }) {
  const [value, setValue] = useState("");

  const submit = (e) => {
    e.preventDefault();
    onSearch?.(value.trim());
  };

  return (
    <div className="searchbar">
      <form onSubmit={submit}>
        <div className="search-input-wrap">
          <Search size={15} />
          <input
            type="text"
            placeholder="Search equipment, failures, suppliers…"
            value={value}
            onChange={(e) => setValue(e.target.value)}
            aria-label="Search entities"
          />
        </div>
        <button type="submit" className="btn-search" aria-label="Run search">
          Search
        </button>
      </form>
    </div>
  );
}
