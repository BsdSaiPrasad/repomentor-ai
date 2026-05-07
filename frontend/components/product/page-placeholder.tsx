import Link from "next/link";

export function PagePlaceholder({
  title,
  description,
  note,
}: {
  title: string;
  description: string;
  note: string;
}) {
  return (
    <div className="flex min-h-dvh flex-col bg-background">
      <div className="mx-auto flex w-full max-w-5xl flex-1 flex-col px-6 py-10">
        <div className="mb-10">
          <h1 className="text-3xl font-semibold tracking-tight text-foreground">
            {title}
          </h1>
          <p className="mt-3 max-w-2xl text-sm leading-7 text-muted-foreground">
            {description}
          </p>
        </div>

        <div className="rounded-2xl border border-border/40 bg-card/40 p-6">
          <p className="text-sm leading-7 text-foreground">{note}</p>
          <div className="mt-5">
            <Link
              className="text-sm font-medium text-primary underline-offset-4 hover:underline"
              href="/"
            >
              Open Course Assistant
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
