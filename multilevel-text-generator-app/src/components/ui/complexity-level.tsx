interface Props {
    levelName: string
    active: boolean
};

export default function ComplexityLevel({ levelName, active }: Props) {
    return (
        <div className="flex flex-col w-full gap-y-2 text-content-muted text-[.7rem]">
            <div className={
                active
                    ? "rounded-full w-full h-1.5 max-h-2 bg-primary transition-colors duration-300"
                    :
                    "rounded-full w-full h-1.5 max-h-2 bg-content-muted/35 transition-colors duration-300"
            }
            >
            </div>
            <p className={active ? "text-primary font-bold" : "text-content-muted"}>{levelName}</p>
        </div >
    )
}

